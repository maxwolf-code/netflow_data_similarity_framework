import argparse
import pandas as pd
from os import listdir, makedirs

def read_csv_data(path, skip_errors=False, index_col=None, header=0, nrows=None, use_cols=None):
    """Read csv data using pandas

    Args:
        path (str): path to the csv file
        skip_errors (bool, optional): stop parsing on errors. Defaults to False.
        index_col (str/int, optional): index of dataframe in csv. Defaults to None.
        header (int, optional): headers of the dataframe in csv. Defaults to 0.
        nrows (int, optional): number of rows to read. Defaults to None.

    Returns:
        DataFrame: pandas DF with csv content
    """
    print('READ: %s', path)
    df = pd.read_csv(path, on_bad_lines='skip', index_col=index_col, header=header, nrows=nrows, usecols=use_cols) #skips bad lines with wrong number of cols

    print('\tSHAPE: %s', str(df.shape))
    print('\tCOLUMS: %s', str(df.columns))
    return df

def draw_and_store_samples(load_path, store_path, n_samples):
    ### create dataset samples ###
    #prefix = './test_samples/real/'
    makedirs(store_path, exist_ok=True)
    df_1 = read_csv_data(load_path)
    #remove path
    ds = load_path.split('/')[-1]
    #remove csv
    ds = ds.split('.')[0]
    for i in range(n_samples):
        #print(i)
        #quit()
        file_name = ds+'_'+str(i)+'.csv'
        #print(file_name)
        sample_df = df_1.sample(n=10000, axis=0)
        counts = sample_df['Label'].value_counts()
        #print(f, counts[1])
        if len(counts)<2:
            #print(f)
            print("only one label in "+file_name)
        print("store sample: "+store_path+file_name)
        sample_df.to_csv(store_path+file_name, header=True, index=False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--load_path", required=True)
    parser.add_argument("-s", '--store_path', required=True)

    args = parser.parse_args()
    load_path = args.load_path
    store_path = args.store_path

    CHUNKS = 30
    draw_and_store_samples(load_path, store_path, CHUNKS)

    #python create_samples.py -l '../../Datasets/Queensland_NetFlow/NetFlow_Benchmark/NF-ToN-IoT.csv' -s './test_samples/real/'