import pandas as pd
from os import makedirs, listdir
import csv

def check_ip(value):
    try:
        octs =  str(value).split('.')
        if len(octs) != 4:
            return False
        for oct in octs:
            if len(oct)<1 or int(oct) < 0 or int(oct) > 255:
                return False
        return True
    except:
        return False
        
def check_port(value):
    try:
        if int(value) > 2**32:
            return False
        if int(value) < -1:
            return False
        return True
    except:
        return False

def check_label(value):
    try:
        if int(value) == 0:
            return True
        if int(value) == 1:
            return True
        else:
            return False
    except: 
        return False

def check_number_float(value):
    try:
        if float(value) >= 0: 
            return True
        else:
            return False
    except:
        return False
    
#TODO check protocol & flags
#def check_tcp_flags(protocol, flags):
#    UDP = 17
#    TCP = 6
#    ICMP = 1
#    IGMP = 2
#    try:
#        if int(flags) > 0:
#            if protocol == TCP:
#                return True
#            else:
#                return False
#        else:
#            return True
#    except:
#        False
def check_tcp_flags(protocol, flags):
    UDP = 17
    TCP = 6
    ICMP = 1
    IGMP = 2
    try:
        if int(flags) > 0:
            if protocol == UDP:
                return False
            else:
                return True
        else:
            return True
    except:
        False

#TODO check if not all packets and bytes are 0
def check_sum_in_out(in_data, out_data):
    try:
        if ( int(in_data) +int(out_data) ) > 0:
            return True
        else: 
            return False
    except: 
        return False


#TODO check logic of error checks above - return False if error is detected! otherwise True?

def check_netflows(df, target_columns):
    row_list = []
    error_count = 0

    #error_count_dict = {'Flows':0, 'IP':0, 'Port':0, 'Protocol':0, 'Bytes':0, 'Packets':0, 'Flags':0, 'Duration':0, 'Label':0}
    #construct dict
    error_count_dict = {'Flows':0, 'In_out_bytes':0, 'In_out_pckts':0, 'Protocol_flags':0}
    for col in target_columns:
        error_count_dict.update({col:0})
    #TODO error count for each attribute instead of data type wise? -> better for detailed analysis -> use column targets?
    
    for row in df.itertuples():
        #try:
        #src
        src_ip = check_ip(row.IPV4_SRC_ADDR)
        if not src_ip:
            error_count_dict['IPV4_SRC_ADDR']+=1
        #src
        src_pt = check_port(row.L4_SRC_PORT)
        if not src_pt:
            error_count_dict['L4_SRC_PORT']+=1
        #dst
        dst_ip = check_ip(row.IPV4_DST_ADDR)
        if not dst_ip:
            error_count_dict['IPV4_DST_ADDR']+=1
        #dst
        dst_pt = check_port(row.L4_DST_PORT)
        if not dst_pt:
            error_count_dict['L4_DST_PORT']+=1
        #proto
        proto = check_number_float(row.PROTOCOL)
        if not proto:
            error_count_dict['PROTOCOL']+=1
        #l7 proto
        #l_proto = check_number_float(row[6])
        #in bytes
        in_bytes = check_number_float(row.IN_BYTES)
        if not in_bytes:
            error_count_dict['IN_BYTES']+=1
        #out bytes
        out_bytes = check_number_float(row.OUT_BYTES)
        if not out_bytes:
            error_count_dict['OUT_BYTES']+=1
        #in pkts
        in_pkts = check_number_float(row.IN_PKTS)
        if not in_pkts:
            error_count_dict['IN_PKTS']+=1
        #out pkts
        out_pkts = check_number_float(row.OUT_PKTS)
        if not out_pkts:
            error_count_dict['OUT_PKTS']+=1
        #flags
        flags = check_number_float(row.TCP_FLAGS)
        if not flags:
            error_count_dict['TCP_FLAGS']+=1
        #duraton
        duration = check_number_float(row.FLOW_DURATION_MILLISECONDS)
        if not duration:
            error_count_dict['FLOW_DURATION_MILLISECONDS']+=1
        #labels
        label = check_label(row.Label)
        if not label:
            error_count_dict['Label']+=1


        in_out_bytes = check_sum_in_out(row.IN_BYTES, row.OUT_BYTES)
        if not in_out_bytes:
            error_count_dict['In_out_bytes']+=1
        
        in_out_pckts = check_sum_in_out(row.IN_PKTS, row.OUT_PKTS)
        if not in_out_pckts:
            error_count_dict['In_out_pckts']+=1

        protcol_flags = check_tcp_flags(row.PROTOCOL, row.TCP_FLAGS)
        if not protcol_flags:
            error_count_dict['Protocol_flags']+=1

        

        if src_ip and src_pt and dst_ip and dst_pt and proto and in_bytes and out_bytes and in_pkts and out_pkts and flags and duration and label and in_out_bytes and in_out_pckts and protcol_flags:
            row_list.append(row[1:]) #drop index
        else:
            #print('ERROR', row)
            #error_count+=1
            error_count_dict['Flows']+=1
        #except:
        #    print('Except ERROR: ', row)
        #    #error_count+=1
        #    error_count_dict['Flows']+=1
    #quit()


    clean_df = pd.DataFrame(row_list)
    #print("ERRORS", error_count)
    return clean_df, error_count_dict

def remove_syntax_erros_files(load_path, store_path, model):
    COLUMNS_TARGET = [ 'IPV4_SRC_ADDR', 'L4_SRC_PORT', 'IPV4_DST_ADDR', 'L4_DST_PORT',
                                'PROTOCOL', 
                                #'L7_PROTO', #GPT
                                'IN_BYTES', 'OUT_BYTES', 
                                'IN_PKTS', 'OUT_PKTS',
                                'TCP_FLAGS', 
                                'FLOW_DURATION_MILLISECONDS', 
                                'Label', 
                                #'Attack' #GPT
    ]
    prefix_store_data = store_path+'/'+model+'/checked_data/'
    makedirs(prefix_store_data, exist_ok=True)
    prefix_error_counts = store_path+'/'+model+'/error_counts/'
    makedirs(prefix_error_counts, exist_ok=True)
    #files = listdir(load_path)
    error_counts_list = []

    #for file in files:
    file = load_path.split('/')[-1]
    if '.txt' in load_path or '.csv' in load_path:
        df = pd.read_csv(load_path, usecols=COLUMNS_TARGET, on_bad_lines='skip', quoting=csv.QUOTE_NONE, nrows=10000, header=0)
        #df = pd.read_csv(path, on_bad_lines='skip', quoting=csv.QUOTE_NONE, nrows=10000, header=0)
        #print(df)
        #quit()
        clean_df, error_count_dict = check_netflows(df, COLUMNS_TARGET)

        error_count_dict.update({'file':load_path})
        error_count_dict = pd.Series(error_count_dict)
        error_counts_list.append(error_count_dict)
        if (len(clean_df)>0):
            clean_df.columns=COLUMNS_TARGET
            clean_df.to_csv(prefix_store_data+file, header=True, index=False)

    error_counts = pd.concat(error_counts_list, ignore_index=True, axis=1).T
    error_counts['model'] = model
    error_counts.to_csv(prefix_error_counts+file, header=True, index=False)


def split_ds_file(df):
        print(df.file)
        df['ds'] = df['file'].str.split('/').str[-1].str.split('_').str[0]
        print(df.ds)
        if any('real' in s for s in list(df.model.unique())):
            df['step'] = 0
        else:
            df['step'] = df['file'].str.split('/').str[-1].str.split('_').str[1].str.split('-').str[1].str.split('.').str[0].astype(int)
        #df = df.set_index('step')
        return df

def aggreate_error_counts(path, path_out):
    file_list = []
    for file in listdir(path):
        print(file)
        df = pd.read_csv(path+file, header=0)
        print(df)
        df = split_ds_file(df)
        file_list.append(df.copy())
    df_all = pd.concat(file_list, axis=0)
    df_all.to_csv(path_out, header=True, index=False)


if __name__ == '__main__':
   
    for model in ['gpt2', 'wgan', 'wganbin']:

        prefix = '../../Datasets/Queensland_NetFlow/synthetic/'

        load_path = prefix + model+'_data_clean/'
        store_path = prefix + model+'_data_checked/'

        remove_syntax_erros_files(load_path, store_path, model)







