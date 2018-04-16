import h5py
import pandas as pd
import numpy as np

def importrepstruct(filename):
    #import mat files with spectral information contained in structures into panda data frame
    var = filename.split('/')[-1].split('.')[0]
    f = h5py.File(filename,'r')
    struarray  = f[var]
    struct = {key:[] for key in struarray.keys()}
    for k in struarray.keys():
        for n in range(struarray[k].shape[0]):
            if k == 'fn' or k == 'filename':
                struct[k].append(f[struarray[k][n, 0]].value.tobytes()[::2].decode())
            else:
                struct[k].append(f[struarray[k][n, 0]].value.flatten())
        numelem = [len(x) for x in struct[k]]
        if numelem[1:] == numelem[:-1] and max(numelem) == 1:
            struct[k] = np.concatenate(struct[k]).ravel()
    df = pd.DataFrame(struct)
    f.close()
    return df

if __name__ == "__main__":
    filename = '/opt/data/o93o75/analysis/data_structures/fv_repA_3_18_2013_sal.mat'
    df = importstruct(filename)