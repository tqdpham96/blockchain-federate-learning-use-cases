import numpy as np
import math

# — sequence utilities —————————————————————————————————————————————————————————————————————————————

def running_mean(x: np.ndarray, N: int) -> np.ndarray:
    c = np.cumsum(np.insert(x, 0, 0))
    return (c[N:] - c[:-N]) / float(N)

def gen_sequences(df, seq_length, feature_cols):
    """Yield sliding windows of shape (seq_length, len(feature_cols))."""
    A = df[feature_cols].values
    for start in range(len(A) - seq_length):
        yield A[start:start+seq_length]

def gen_labels(df, seq_length, label_col):
    """Return labels aligned with gen_sequences (drops first seq_length rows)."""
    return df[label_col].values[seq_length:].reshape(-1,1)


# — hinge loss / gradients / metrics —————————————————————————————————————————————————————————————————

def hinge_loss(w, X, y):
    m = 1 - y * (X @ w)
    return np.maximum(0, m)

def grad_full(w, X, y, lam):
    N = X.shape[0]
    losses = hinge_loss(w, X, y).flatten()
    mask = (losses > 0).astype(float).reshape(-1,1)
    g = - (mask * y * X).sum(axis=0, keepdims=True).T / N
    return g + 2*lam*w

def grad_point(w, x_i, y_i, lam):
    loss = 1 - float(y_i * (x_i @ w))
    if loss <= 0:
        gh = np.zeros_like(w)
    else:
        gh = -(y_i * x_i).T
    return gh + 2*lam*w

def predict(w, X):
    return np.sign(X @ w)

def accuracy(w, X, y):
    return float((predict(w, X)==y).mean())


# — optimizers ————————————————————————————————————————————————————————————————————————————————

def gradient_descent(w, Xs, ys, lr, lam, iters):
    M = len(Xs)
    for _ in range(iters):
        G = sum(grad_full(w, Xs[i], ys[i], lam) for i in range(M)) / M
        w = w - lr * G
    return w

def stochastic_gradient_descent(w, Xs, ys, lr, lam, iters):
    M, rng = len(Xs), np.random.default_rng()
    for _ in range(iters):
        grads = []
        for i in range(M):
            idx = rng.integers(Xs[i].shape[0])
            grads.append(grad_point(w, Xs[i][[idx],:], ys[i][[idx],:], lam))
        G = sum(grads) / M
        w = w - lr * G
    return w

def fsvrg(w, Xs, ys, lr, lam, iters, epoch_len=None)-> np.ndarray:
    """
    Federated SVRG: perform `iters` global steps.
    At each step we:
      1) compute full gradient over all workers
      2) perform one SVRG‐style local update per worker
      3) average the locals into new `w`
    If verbose=True, we print the iteration count and the norm of the last
    SVRG update direction.
    """

    M = len(Xs)
    if epoch_len is None:
        epoch_len = iters
    t = 0
    while t < iters:
        full_g = sum(grad_full(w, Xs[i], ys[i], lam) for i in range(M)) / M
        Wloc = np.tile(w, (1,M))
        for _ in range(min(epoch_len, iters-t)):
            for i in range(M):
                N = Xs[i].shape[0]
                idx = np.random.randint(N)
                g_w   = grad_point(Wloc[:,[i]], Xs[i][[idx],:], ys[i][[idx],:], lam)
                g_ref = grad_point(w,           Xs[i][[idx],:], ys[i][[idx],:], lam)
                update_dir = g_w - g_ref + full_g
                Wloc[:,i] -= lr*(g_w - g_ref + full_g).reshape(-1)
            t += 1
            if t>=iters: break
        w = Wloc.mean(axis=1,keepdims=True)
        print(f"FSVRG: Number iterations: {i+1}/{iters}")
        print("FSVRG: final norm:", np.linalg.norm(update_dir))
    return w

# — solver entry point —————————————————————————————————————————————————————————————————————————

def solver(
    X_workers, y_workers,
    X_test, y_test,
    w_init,
    lr=1e-2,
    iters=1000,
    lam=1e-4,
    method='gd',
    epoch_len=None
):
    w = w_init.copy()
    if method=='gd':
        w = gradient_descent(w, X_workers, y_workers, lr, lam, iters)
    elif method=='sgd':
        w = stochastic_gradient_descent(w, X_workers, y_workers, lr, lam, iters)
    elif method=='fsvrg':
        w = fsvrg(w, X_workers, y_workers, lr, lam, iters, epoch_len)
    else:
        raise ValueError(f"Unknown method {method!r}")

    test_acc  = accuracy(w, X_test, y_test)
    test_loss = float(hinge_loss(w, X_test, y_test).sum())
    print(f"[{method.upper()}] test loss={test_loss:.4f}, acc={test_acc:.4%}")
    return w