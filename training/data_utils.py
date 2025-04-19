import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from .lib import gen_sequences, gen_labels  # relative import

def load_train(path, seq_length, feature_cols, w0=30, w1=50, clip_threshold=150):
    df = pd.read_csv(path, sep=' ', header=None)
    df.drop(columns=[26,27], inplace=True)
    df.columns = ['id','cycle','setting1','setting2','setting3'] + [f's{i}' for i in range(1,22)]
    df.drop(columns=['setting3','s1','s5','s6','s10','s16','s18','s19'], inplace=True)

    # compute RUL
    mx = df.groupby('id')['cycle'].max().reset_index()
    mx.columns = ['id','max_cycle']
    df = df.merge(mx, on='id')
    df['RUL'] = df['max_cycle'] - df['cycle']
    df.drop(columns='max_cycle', inplace=True)

    # labels
    df['label1'] = np.where(df['RUL']<=w1, 1, -1)
    df['label2'] = df['label1']
    df.loc[df['RUL']<=w0,'label2']=2

    # normalize
    df['cycle_norm'] = df['cycle']
    cols_norm = df.columns.difference(['id','cycle','RUL','label1','label2'])
    scaler = MinMaxScaler()
    df[cols_norm] = scaler.fit_transform(df[cols_norm])

    # clip RUL
    df['RUL'] = df['RUL'].clip(upper=clip_threshold)
    df.sort_values(['id','cycle'],inplace=True)

    # build sequences per engine
    X_dic, Y_dic, Y_rul_dic = {}, {}, {}
    for eid in df['id'].unique():
        sub = df[df['id']==eid]
        X = np.vstack([s for s in gen_sequences(sub, seq_length, feature_cols)])
        y = gen_labels(sub, seq_length, 'label1')
        r = gen_labels(sub, seq_length, 'RUL').astype(int)
        X_dic[eid]      = X.astype(np.float32)
        Y_dic[eid]      = y.astype(np.float32)
        Y_rul_dic[eid]  = r.reshape(-1,1)

    # truncate to smallest length
    L = min(v.shape[0] for v in Y_rul_dic.values())
    for eid in X_dic:
        X_dic[eid]     = X_dic[eid][-L:]
        Y_dic[eid]     = Y_dic[eid][-L:]
        Y_rul_dic[eid] = Y_rul_dic[eid][-L:]

    return X_dic, Y_dic, Y_rul_dic, scaler

def load_test(path_test, path_truth, seq_length, feature_cols, scaler, w0=30, w1=50):
    df = pd.read_csv(path_test, sep=' ', header=None)
    df.drop(columns=[26,27], inplace=True)
    df.columns = ['id','cycle','setting1','setting2','setting3'] + [f's{i}' for i in range(1,22)]
    df.drop(columns=['setting3','s1','s5','s6','s10','s16','s18','s19'], inplace=True)

    # normalize
    df['cycle_norm'] = df['cycle']
    cols_norm = df.columns.difference(['id','cycle'])
    df[cols_norm] = scaler.transform(df[cols_norm])

    # read true RUL increments
    truth = pd.read_csv(path_truth, sep=' ', header=None).drop(columns=1)
    truth.columns = ['more']
    truth['id'] = truth.index+1

    # absolute RUL
    mx = df.groupby('id')['cycle'].max().reset_index()
    mx.columns = ['id','max_cycle']
    truth = truth.merge(mx, on='id')
    truth['RUL_total'] = truth['max_cycle'] + truth['more']
    truth.drop(columns=['more','max_cycle'], inplace=True)

    df = df.merge(truth, on='id')
    df['RUL'] = df['RUL_total'] - df['cycle']
    df.drop(columns='RUL_total', inplace=True)

    # labels
    df['label1'] = np.where(df['RUL']<=w1, 1, -1)
    df['label2'] = df['label1']
    df.loc[df['RUL']<=w0,'label2']=2
    df.sort_values(['id','cycle'],inplace=True)

    # build sequences
    X_dic, Y_dic, Y_rul_dic = {}, {}, {}
    for eid in df['id'].unique():
        sub = df[df['id']==eid]
        X = np.vstack([s for s in gen_sequences(sub, seq_length, feature_cols)])
        y = gen_labels(sub, seq_length, 'label1')
        r = gen_labels(sub, seq_length, 'RUL').astype(int)
        X_dic[eid]     = X.astype(np.float32)
        Y_dic[eid]     = y.astype(np.float32)
        Y_rul_dic[eid] = r.reshape(-1,1)

    # truncate to smallest length (to match train)
    L = min(v.shape[0] for v in Y_rul_dic.values())
    for eid in X_dic:
        X_dic[eid]     = X_dic[eid][-L:]
        Y_dic[eid]     = Y_dic[eid][-L:]
        Y_rul_dic[eid] = Y_rul_dic[eid][-L:]

    return X_dic, Y_dic, Y_rul_dic