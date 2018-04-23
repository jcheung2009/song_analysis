import h5py
import pandas as pd
import numpy as np

def importrepstruct(filename,condition):
    #import mat files with repeat information contained in structures into panda data frames
    #df1 has variables at trialnumber level, df2 has variables at syllable level
    name = filename.split('/')[-1].split('.')[0]
    f = h5py.File(filename,'r')
    struarray  = f[name]
    # extract values in hdf file into dictionary
    struct = {key: [] for key in struarray.keys()}
    for k in struarray.keys():
        for n in range(struarray[k].shape[0]):
            if k == 'fn' or k == 'filename':
                struct[k].append(f[struarray[k][n, 0]].value.tobytes()[::2].decode())  # convert to string
            elif len(f[struarray[k][n, 0]].shape) == 1:  # for nX0 dim vectors
                struct[k].append([np.nan])
            else:
                struct[k].append(f[struarray[k][n, 0]].value.flatten())
        numelem = [len(x) for x in struct[k]]
        if numelem[1:] == numelem[:-1] and max(numelem) == 1:  # convert to single array if elements
            # all have same size and = 1
            struct[k] = np.concatenate(struct[k]).ravel()
    # create first dataframe for variables with indexing at trialnumber level
    keys = ['datenm', 'firstpeakdistance', 'fn', 'ind', 'runlength', 'sm', 'smtmp']
    df = pd.DataFrame(struct)
    df['name'] = name
    df['condition'] = condition
    df['trialnumber'] = range(len(df))
    df1 = df.set_index(['name', 'condition', 'trialnumber'])[keys]
    # create second dataframe for elements indexing at syllable level
    struct2 = dict()
    syllindex = np.concatenate(np.array([range(len(x)) for x in df.ons.values]))
    trialnumindex = np.concatenate([np.repeat(df.trialnumber[x], len(df.ons[x])) for x in range(len(df))])
    conditionindex = np.repeat(condition, len(trialnumindex))
    nameindex = np.repeat(name, len(conditionindex))
    struct2['syllgaps'] = np.concatenate([np.append(df.syllgaps[x], np.repeat(np.nan, len(df.ons[x]) -
            len(df.syllgaps[x]))) for x in range(len(df.ons))])
    struct2['sylldurations'] = np.concatenate(df.sylldurations)
    struct2['ons'] = np.concatenate(df.ons)
    struct2['off'] = np.concatenate(df.off)
    index = pd.MultiIndex.from_arrays([nameindex, conditionindex, trialnumindex, syllindex],
                                      names=('name', 'condition', 'trialnumber', 'syllindex'))
    df2 = pd.DataFrame(struct2, index=index)

    f.close()
    return df1, df2

if __name__ == "__main__":
    filename = '/opt/data/o93o75/analysis/data_structures/fv_repA_3_18_2013_sal.mat'
    df1,df2 = importrepstruct(filename)