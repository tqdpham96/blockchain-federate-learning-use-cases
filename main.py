import random
import numpy as np
from training.lib         import solver, accuracy
from training.data_utils  import load_train, load_test
from ipfs_upload           import (
    retrieve_weights_from_chain,
    publish_weights_to_ipfs_and_chain
)

def partition_workers(X_dic, Y_dic, num_workers):
    eids = list(X_dic.keys())
    random.shuffle(eids)
    groups = [eids[i::num_workers] for i in range(num_workers)]
    Xw, Yw = [], []
    for g in groups:
        Xw.append(np.vstack([X_dic[e] for e in g]))
        Yw.append(np.vstack([Y_dic[e] for e in g]))
    return Xw, Yw

def dict_to_flat_arrays(X_dic, Y_dic):
    eids = sorted(X_dic)
    X = np.vstack([X_dic[e] for e in eids])
    Y = np.vstack([Y_dic[e] for e in eids])
    return X, Y

def federate_average(models):
    """ Simple average of weight vectors """
    stacked = np.stack([m.flatten() for m in models], axis=1)
    w_avg = np.mean(stacked, axis=1, keepdims=True)
    return w_avg

def main():
    # — experiment parameters —
    train_file  = 'train_FD001.txt'
    test_file   = 'test_FD001.txt'
    truth_file  = 'RUL_FD001.txt'
    seq_len     = 20
    sensor_cols = [
        's2','s3','s4','s7','s8','s9','s11',
        's12','s13','s14','s15','s17','s20','s21'
    ]
    seq_cols    = ['setting1','setting2','cycle_norm'] + sensor_cols
    w0, w1      = 30, 50
    clip_thresh = 150
    num_workers = 10

    lr      = 1e-2
    iters   = 3000
    lam     = 0.1
    local_method = 'gd'       # local train
    epoch_len    = 20
    fed_method   = 'fsvrg'    # global federated

    # — load & preprocess —
    X_train_dic, Y_train_dic, _, scaler = load_train(
        train_file, seq_len, seq_cols, w0, w1, clip_thresh
    )
    X_test_dic,  Y_test_dic,  _        = load_test(
        test_file, truth_file, seq_len, seq_cols, scaler, w0, w1
    )

    # — partition to workers & flatten test —
    X_workers, Y_workers = partition_workers(X_train_dic, Y_train_dic, num_workers)
    X_test, Y_test       = dict_to_flat_arrays(X_test_dic, Y_test_dic)

    # — per‐worker local training + push to IPFS/chain —
    print("▶▶ Starting local worker trainings …")
    for wid, (Xw, Yw) in enumerate(zip(X_workers, Y_workers), start=1):
        print(f"\n--- Worker {wid}/{num_workers} local SVM training ---")
        d      = Xw.shape[1]
        w_init = np.random.randn(d,1)
        # train local model
        w_local = solver(
            [Xw], [Yw], X_test, Y_test,
            w_init, lr=lr, iters=iters, lam=lam,
            method=local_method, verbose=False
        )
        # publish
        publish_weights_to_ipfs_and_chain(w_local, key=wid)

    # later, retrieve them all
    models = []
    for wid in range(1, num_workers+1):
        w_i = retrieve_weights_from_chain(wid)
        models.append(w_i)

    # — now read them back and federate-average —
    print("\n▶▶ Fetching all worker models from chain + IPFS …")
    models = retrieve_weights_from_chain(num_workers)
    w_avg = federate_average(models)

    # — evaluate the simple average —
    avg_acc = accuracy(w_avg, X_test, Y_test)
    print(f"\n✅ Simple Fed‑Avg test accuracy: {avg_acc:.4%}")

    # — run FL solver init’ed at w_avg —
    print("\n▶▶ Starting federated refinement (FSVRG) from Fed‑Avg init …")
    w_final = solver(
        X_workers, Y_workers,
        X_test, Y_test,
        w_avg,
        lr=lr, iters=iters, lam=lam,
        method=fed_method, epoch_len=epoch_len,
        verbose=True
    )
    final_acc = accuracy(w_final, X_test, Y_test)
    print(f"\n✅ FSVRG‑refined test accuracy: {final_acc:.4%}")

if __name__ == '__main__':
    main()