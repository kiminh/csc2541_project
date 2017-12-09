import numpy as np

def load_R():
    from movieLensAnalyzer import MovieLensAnalyzer
    movieLensAnalyzer = MovieLensAnalyzer()
    R_train = movieLensAnalyzer.trainRatingMatrix
    R_test = movieLensAnalyzer.testRatingMatrix

    R = R_train + R_test
    print("R contains {} ratings".format(np.sum(R>0)))
    return R


def _desparsify(R, MIN_PERC_FILLED_ITEMS, MIN_PERC_FILLED_USERS):
    print("Before desparsify: % of items: ", np.sum(R > 0) / (R.shape[0] * R.shape[1]))

    R_dense = np.copy(R)

    idx = []
    # Remove items
    for j in range(R_dense.shape[1]):
        perc_filled = np.sum(R_dense[:,j] > 0) / R_dense.shape[0]
        if perc_filled >= MIN_PERC_FILLED_ITEMS:
            idx.append(j)
    R_dense = R_dense[:, idx]
    R_dense.shape

    idx = []
    # Remove users
    for i in range(R_dense.shape[0]):
        perc_filled = np.sum(R_dense[i,:] > 0) / R_dense.shape[1]
        if perc_filled >= MIN_PERC_FILLED_USERS:
            idx.append(i)
    R_dense = R_dense[idx, :]
    R_dense.shape

    print("After desparsify: % of items: ", np.sum(R_dense > 0) / (R_dense.shape[0] * R_dense.shape[1]))
    print("Size: ", R_dense.shape)
    return R_dense


def desparsify(R):
    '''
    Before desparsify: % of items:  0.0630466936422
    After desparsify: % of items:  0.555527743012
    Size:  (510, 47)
    '''
    return _desparsify(R, MIN_PERC_FILLED_ITEMS=0.3, MIN_PERC_FILLED_USERS=0.3)


def desparsify_2(R):
    '''
    Before desparsify: % of items:  0.0630466936422
    After desparsify: % of items:  0.373593572446
    Size:  (354, 353)
    '''
    return _desparsify(R, MIN_PERC_FILLED_ITEMS=0.1, MIN_PERC_FILLED_USERS=0.2)


def prepare_test_users(R, NUM_USERS_DENSE = 20, NUM_USERS_SPARS = 20, PERC_DROP = 0.3):
    rating_density_per_user = list(zip(np.sum(R>0, axis=1), range(R.shape[0])))
    dense_users = sorted(rating_density_per_user, key=lambda x: -x[0])[:NUM_USERS_DENSE]
    spars_users = sorted(rating_density_per_user, key=lambda x:  x[0])[:NUM_USERS_SPARS]

    train_mask = R > 0

    # The test masks we'll use later.
    test_masks = {}

    # We artifically dropout some elements from the users we're interested in. Assume the rest of the matrix is filled.
    np.random.seed(1337)
    for _, idx in (dense_users + spars_users):
        before = np.copy(train_mask[idx, :])

        dropout = 1-np.random.binomial(1, PERC_DROP, size=R.shape[1])
        train_mask[idx, :] = dropout * train_mask[idx, :]

        test_mask = np.bitwise_xor(before, train_mask[idx, :])
        test_masks[idx] = test_mask

    return dense_users, spars_users, train_mask, test_masks