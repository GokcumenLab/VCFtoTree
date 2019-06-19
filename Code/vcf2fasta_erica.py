# input is vcf file, and a reference sequence to the interested region
# output is file with aligned haplotypes for all the 2504 individuals
# error is the output of structural variations
# Same function as Pavlos perl script
# This code use a reference sequence, transform vcf file to an aligned fasta file.
# It fixed the error that INDELs can have alternative allele 2 and 3 now.
# It can process "VT=SNP,INDEL" this kind of weirdo now.
# Usage: python vcf2fasta_erica.py yourvcffile.vcf reference_sequence.fa 111111 222222 aligned_fasta.fa error_sv
# phase3 2504, phase1 1092

# Fixed repetitive locus with the same chromosome location;
# Fixed the deleting INDELs, it will substitute the reference with "-".
# fixed multi-allelic indels.

import sys
import re
import string
import collections  # for sorting the dic by key
import time
import datetime

startTime = time.time()

if len(sys.argv) != 8:
    print "Usage: python vcf2fasta_erica.py [inputvcf] [Reference sequence] [start] [end] [population_list] [output] [error]"
    sys.exit(1)

input = open(sys.argv[1], 'r')
ref_seq = open(sys.argv[2], 'r')
start = int(sys.argv[3])
end = int(sys.argv[4])
pop_list = str(sys.argv[5])
output = open(sys.argv[6], 'w')
# output structural variation (VT=SV) as ERROR message.
error = open(sys.argv[7], 'w')

haplo = {}
freq = {}
all_haplo = {}  # summary/final haplotype sequence dic for everyone
input2 = []  # a cleaner vcf without header, without SV, and indels already aligned with "--"

r_seq = []
for r0 in ref_seq:
    r1 = r0.replace('\n', '')
    if r1.startswith('>'):
        continue
    r_seq.append(r1)
r = ''.join(r_seq)  # reference sequence without '\n'

# output.write('>reference_hg19\n'+r+'\n')

ref_bs = {}  # ref_seq dictionary file
count = 0
while count <= (len(r) - 1):
    ref_bs[str(start + count)] = r[count]
    count = count + 1
# for r in ref_bs.keys():
#    ref_bs[int(r)] = ref_bs[r]
#    del ref_bs[r]
# ref_bs = collections.OrderedDict(sorted(ref_bs.items()))  #sort reference sequence
# print ref_bs


input_temp = []
for line in input:
    line = line.strip()
    if line.startswith('##'):
        continue
    elif line.startswith('#C'):
        id = []
        # id[9] - id[2062] are the individual id (PHASE3); id[9] - id[1100] phase1
        id = line.split('\t')
        continue
    input_temp.append(line)

# check if this line locus are the same with the previous one, combining two same locus
input_cnt = 0
while input_cnt <= len(input_temp) - 1:

    l_now = input_temp[input_cnt]
    info_now = []
    if 'VT=SV' in l_now:
        input_temp.remove(input_temp[input_cnt])
        error.write(l_now + '\n')
        continue

    gt_now = []
    gt_now = l_now.split('\t')

    gt_pre = []
    l_pre = input_temp[input_cnt - 1]
    gt_pre = l_pre.split('\t')

    if not ',' in gt_pre[4]:
        cnt_comma = 0
    else:
        cnt_comma = 1

    if gt_pre[1] == gt_now[1]:
        if gt_now[3] != gt_pre[3]:
            if len(gt_pre[3]) <= len(gt_now[3]):
                delta_temp = len(gt_now[3]) - len(gt_pre[3])
                gt_pre[4] = gt_pre[4] + gt_now[3][-delta_temp:]
                gt_pre[3] = gt_now[3]

        gt_pre[2] = ','.join([gt_pre[2], gt_now[2]])
        gt_pre[4] = ','.join([gt_pre[4], gt_now[4]])

        gt_now_gtonly = '\t'.join(gt_now[9:])

        if cnt_comma == 0:
            replaced = gt_now_gtonly.replace('1', '2')
            gt_now[9:] = replaced.split('\t')
        else:
            replaced = gt_now_gtonly.replace('1', '3')
            gt_now[9:] = replaced.split('\t')

        m = 1
        while m <= 2504:
            new_gt1 = max(gt_pre[8 + m][0], gt_now[8 + m][0])
            new_gt2 = max(gt_pre[8 + m][-1], gt_now[8 + m][-1])
            gt_pre[8 + m] = new_gt1 + '|' + new_gt2
            m += 1

        # gt_pre[7].replace('VT=SNP','VT=SNP,INDEL')
        info_pre = gt_pre[7].split(';')
        for y in info_pre:
            if y == 'VT=SNP':
                gt_pre[7] = gt_pre[7].replace('VT=SNP', 'VT=SNP,INDEL')
            elif y == 'VT=INDEL':
                gt_pre[7] = gt_pre[7].replace('VT=INDEL', 'VT=SNP,INDEL')
            elif y == 'VT=SNP,INDEL':
                # .replace('VT=INDEL,INDEL', 'VT=SNP,INDEL')
                gt_pre[7] = gt_pre[7]

        input_temp[input_cnt - 1] = '\t'.join(gt_pre)
        input_temp.remove(input_temp[input_cnt])
    else:
        # print input_cnt, len(input_temp)
        input_cnt += 1

input2 = []

for l in input_temp:

    info0 = []
    gt0 = []
    gt0 = l.split('\t')

    info0 = gt0[7].split(';')
    for x in info0:
        if x.startswith('VT='):
            vt = x
            if vt == 'VT=SV':
                error.write(l + '\n')
            elif vt == 'VT=SNP,INDEL':
                if not any(',' in gt0[4] for c0 in gt0[4]):
                    delta = len(gt0[3]) - len(gt0[4])
                    if delta > 0:
                        gt0[4] = gt0[4] + delta * '-'
                        l = '\t'.join(gt0)
                        input2.append(l)
                        error.write(l + '\n')
                    elif delta < 0:
                        gt0[3] = gt0[3] + (-delta * '-')
                        l = '\t'.join(gt0)
                        input2.append(l)
                        error.write(l + '\n')
                else:
                    alter0 = gt0[4].split(',')
                    num_alter = len(alter0)
                    if num_alter == 2:
                        max_len = max(len(gt0[3]), len(
                            alter0[0]), len(alter0[1]))
                        delta_0 = max_len - len(gt0[3])
                        delta_1 = max_len - len(alter0[0])
                        delta_2 = max_len - len(alter0[1])
                        gt0[3] = gt0[3] + delta_0 * '-'
                        gt0[4] = alter0[0] + delta_1 * '-' + \
                            ',' + alter0[1] + delta_2 * '-'
                        l = '\t'.join(gt0)
                        input2.append(l)
                        error.write(l + '\n')
                    elif num_alter == 3:
                        max_len = max(len(gt0[3]), len(
                            alter0[0]), len(alter0[1]), len(alter0[2]))
                        delta_0 = max_len - len(gt0[3])
                        delta_1 = max_len - len(alter0[0])
                        delta_2 = max_len - len(alter0[1])
                        delta_3 = max_len - len(alter0[2])
                        gt0[3] = gt0[3] + delta_0 * '-'
                        gt0[4] = alter0[0] + delta_1 * '-' + ',' + alter0[1] + delta_2 * '-' + ',' + alter0[
                            2] + delta_3 * '-'
                        l = '\t'.join(gt0)
                        input2.append(l)
                        error.write(l + '\n')
                    else:
                        print alter0
                        print "Please go to find Erica..."

            elif vt == 'VT=INDEL':
                if not any(',' in gt0[4] for c0 in gt0[4]):
                    # gt[3] is REF, gt[4] is ALT
                    delta = len(gt0[3]) - len(gt0[4])
                    if delta > 0:
                        gt0[4] = gt0[4] + delta * '-'
                        l = '\t'.join(gt0)
                        input2.append(l)
                        error.write(l + '\n')
                    elif delta < 0:
                        gt0[3] = gt0[3] + (-delta * '-')
                        l = '\t'.join(gt0)
                        input2.append(l)
                        error.write(l + '\n')
                else:
                    alter0 = gt0[4].split(',')
                    indel_cnt = len(alter0)
                    if indel_cnt == 2:
                        max_len = max(len(gt0[3]), len(
                            alter0[0]), len(alter0[1]))
                        delta_0 = max_len - len(gt0[3])
                        delta_1 = max_len - len(alter0[0])
                        delta_2 = max_len - len(alter0[1])
                        gt0[3] = gt0[3] + delta_0 * '-'
                        gt0[4] = alter0[0] + delta_1 * '-' + \
                            ',' + alter0[1] + delta_2 * '-'
                    elif indel_cnt == 3:
                        max_len = max(len(gt0[3]), len(
                            alter0[0]), len(alter0[1]), len(alter0[2]))
                        delta_0 = max_len - len(gt0[3])
                        delta_1 = max_len - len(alter0[0])
                        delta_2 = max_len - len(alter0[1])
                        delta_3 = max_len - len(alter0[2])
                        gt0[3] = gt0[3] + delta_0 * '-'
                        gt0[4] = alter0[0] + delta_1 * '-' + ',' + alter0[1] + delta_2 * '-' + ',' + alter0[
                            2] + delta_3 * '-'
                    elif indel_cnt == 4:
                        max_len = max(len(gt0[3]), len(alter0[0]), len(
                            alter0[1]), len(alter0[2]), len(alter0[3]))
                        delta_0 = max_len - len(gt0[3])
                        delta_1 = max_len - len(alter0[0])
                        delta_2 = max_len - len(alter0[1])
                        delta_3 = max_len - len(alter0[2])
                        delta_4 = max_len - len(alter0[3])
                        gt0[3] = gt0[3] + delta_0 * '-'
                        gt0[4] = alter0[0] + delta_1 * '-' + ',' + alter0[1] + delta_2 * '-' + ',' + alter0[
                            2] + delta_3 * '-' + ',' + alter0[3] + delta_4 * '-'

                    l = '\t'.join(gt0)
                    input2.append(l)
                    error.write(l + '\n')
            elif vt == 'VT=SNP':
                input2.append(l)
            else:
                print vt
                print "Please go to find Erica..."
error.close()

n = 1
while n <= 2504:  # phase3 2504, phase1 1092
    # print n
    dic_psn1 = {}
    dic_psn2 = {}
    # dic_psn1 = ref_bs  # {}  # variation/sequence dictionary for each individual, initial value is same as ref_bs
    dic_psn2 = ref_bs  # everyone has two dic for two haplotypes respectably
    for k1 in ref_bs.keys():  # .keys() would introduce a iteration
        dic_psn1[k1 + '_1'] = ref_bs[k1]
    for line in input2:
        gt = []
        gt = line.split('\t')
        pos = gt[1]  # position is gt[1]

        if any(',' in gt[4] for c in gt[4]):
            alter = gt[4].split(',')
            if gt[8 + n][0] == '0':
                gt1 = gt[3]
            elif gt[8 + n][0] == '1':
                gt1 = alter[0]  # gt[4][0]
                # print gt1
            elif gt[8 + n][0] == '2':
                gt1 = alter[1]  # gt[4][2]
            elif gt[8 + n][0] == '3':
                gt1 = alter[2]  # gt[4][3]
            elif gt[8 + n][0] == '4':
                gt1 = alter[3]
            if gt[8 + n][2] == '0':
                gt2 = gt[3]
            elif gt[8 + n][2] == '1':
                gt2 = alter[0]  # gt[4][0]
            elif gt[8 + n][2] == '2':
                gt2 = alter[1]  # gt[4][2]
            elif gt[8 + n][2] == '3':
                gt2 = alter[2]  # gt[4][3]
            elif gt[8 + n][2] == '4':
                gt2 = alter[3]
        else:
            if gt[8 + n][0:3] == '0|0':
                gt1 = gt[3]
                gt2 = gt[3]
            elif gt[8 + n][0:3] == '1|0':
                gt1 = gt[4]
                gt2 = gt[3]
            elif gt[8 + n][0:3] == '0|1':
                gt1 = gt[3]
                gt2 = gt[4]
            elif gt[8 + n][0:3] == '1|1':
                gt1 = gt[4]
                gt2 = gt[4]
            else:
                print 'error'

        # if len(gt1) <= len(dic_psn1[pos+'_1']):
        #    continue

        # dic_psn1[pos] = gt1
        # dic_psn2[pos] = gt2
        # if n==1:
        #    print pos
        #    print dic_psn1['171117907_1']

        # deal with len(reference allele) > 1
        if len(gt[3]) > 1:
            if not '-' in gt[3]:
                len_ref = len(gt[3])
                for pos_key in range(int(pos), int(pos) + len_ref):
                    dic_psn1[str(pos_key) + '_1'] = gt1[pos_key - int(pos)]
                    dic_psn2[str(pos_key)] = gt2[pos_key - int(pos)]
            elif gt[3][1] == '-':
                dic_psn1[pos + '_1'] = gt1
                dic_psn2[pos] = gt2
            else:
                gap_cnt = gt[3].count('-')
                bp_cnt = len(gt[3]) - gap_cnt
                # print gap_cnt, bp_cnt
                for pos_key in range(int(pos), int(pos) + bp_cnt):
                    dic_psn1[str(pos_key) + '_1'] = gt1[pos_key - int(pos)]
                    dic_psn2[str(pos_key)] = gt2[pos_key - int(pos)]

                gt1_makeup = []
                gt2_makeup = []
                gt1_makeup = gt1[bp_cnt - 1:]
                gt2_makeup = gt2[bp_cnt - 1:]
                target_loc = str(int(pos) + bp_cnt - 1)
                dic_psn1[target_loc + '_1'] = gt1_makeup
                dic_psn2[target_loc] = gt2_makeup
        else:
            dic_psn1[pos + '_1'] = gt1
            dic_psn2[pos] = gt2

            # if pos == '171117899' and n ==1:
            #    print dic_psn1['171117907_1'], dic_psn2['171117907']

            # if n == 1:
            # print dic_psn1['171117907'+'_1'], dic_psn2['171117907']

    haplotype1 = []
    haplotype2 = []
    dic_psn1_sorted = collections.OrderedDict(sorted(dic_psn1.items()))
    dic_psn2_sorted = collections.OrderedDict(sorted(dic_psn2.items()))

    locList = []
    for eachLoc in dic_psn2.keys():
        locList.append(int(eachLoc))

    locList = sorted(locList)

    for p in locList:
        haplotype1.append(dic_psn1_sorted[str(p) + '_1'])
    for q in locList:
        haplotype2.append(dic_psn2_sorted[str(q)])
    all_haplo[id[n + 8] + '.1'] = ''.join(haplotype1)
    all_haplo[id[n + 8] + '.2'] = ''.join(haplotype2)
    n += 1

# Only output selected populations
pop_dic = {'acb': ['HG01879', 'HG01880', 'HG01881', 'HG01882', 'HG01883', 'HG01884', 'HG01885', 'HG01886', 'HG01887',
                   'HG01888', 'HG01889', 'HG01890', 'HG01891', 'HG01894', 'HG01895', 'HG01896', 'HG01897', 'HG01912',
                   'HG01914', 'HG01915', 'HG01916', 'HG01956', 'HG01958', 'HG01959', 'HG01960', 'HG01985', 'HG01986',
                   'HG01987', 'HG01988', 'HG01989', 'HG01990', 'HG02009', 'HG02010', 'HG02011', 'HG02012', 'HG02013',
                   'HG02014', 'HG02051', 'HG02052', 'HG02053', 'HG02054', 'HG02055', 'HG02095', 'HG02107', 'HG02108',
                   'HG02111', 'HG02143', 'HG02144', 'HG02145', 'HG02255', 'HG02256', 'HG02257', 'HG02258', 'HG02280',
                   'HG02281', 'HG02282', 'HG02283', 'HG02284', 'HG02307', 'HG02308', 'HG02309', 'HG02314', 'HG02315',
                   'HG02316', 'HG02317', 'HG02318', 'HG02321', 'HG02322', 'HG02323', 'HG02325', 'HG02330', 'HG02332',
                   'HG02334', 'HG02337', 'HG02339', 'HG02343', 'HG02419', 'HG02420', 'HG02427', 'HG02428', 'HG02429',
                   'HG02433', 'HG02436', 'HG02439', 'HG02442', 'HG02445', 'HG02449', 'HG02450', 'HG02451', 'HG02455',
                   'HG02470', 'HG02471', 'HG02476', 'HG02477', 'HG02478', 'HG02479', 'HG02480', 'HG02481', 'HG02484',
                   'HG02485', 'HG02486', 'HG02489', 'HG02496', 'HG02497', 'HG02501', 'HG02502', 'HG02505', 'HG02508',
                   'HG02511', 'HG02536', 'HG02537', 'HG02541', 'HG02545', 'HG02546', 'HG02547', 'HG02549', 'HG02554',
                   'HG02555', 'HG02557', 'HG02558', 'HG02559', 'HG02577', 'HG02580'],
           'chs': ['HG00403', 'HG00404', 'HG00405', 'HG00406', 'HG00407', 'HG00408', 'HG00409', 'HG00410', 'HG00411',
                   'HG00418', 'HG00419', 'HG00420', 'HG00421', 'HG00422', 'HG00423', 'HG00427', 'HG00428', 'HG00429',
                   'HG00436', 'HG00437', 'HG00438', 'HG00442', 'HG00443', 'HG00444', 'HG00445', 'HG00446', 'HG00447',
                   'HG00448', 'HG00449', 'HG00450', 'HG00451', 'HG00452', 'HG00453', 'HG00457', 'HG00458', 'HG00459',
                   'HG00463', 'HG00464', 'HG00465', 'HG00472', 'HG00473', 'HG00474', 'HG00475', 'HG00476', 'HG00477',
                   'HG00478', 'HG00479', 'HG00480', 'HG00500', 'HG00501', 'HG00502', 'HG00512', 'HG00513', 'HG00514',
                   'HG00524', 'HG00525', 'HG00526', 'HG00530', 'HG00531', 'HG00532', 'HG00533', 'HG00534', 'HG00535',
                   'HG00536', 'HG00537', 'HG00538', 'HG00542', 'HG00543', 'HG00544', 'HG00556', 'HG00557', 'HG00558',
                   'HG00559', 'HG00560', 'HG00561', 'HG00565', 'HG00566', 'HG00567', 'HG00577', 'HG00578', 'HG00579',
                   'HG00580', 'HG00581', 'HG00582', 'HG00583', 'HG00584', 'HG00585', 'HG00589', 'HG00590', 'HG00591',
                   'HG00592', 'HG00593', 'HG00594', 'HG00595', 'HG00596', 'HG00597', 'HG00598', 'HG00599', 'HG00600',
                   'HG00607', 'HG00608', 'HG00609', 'HG00610', 'HG00611', 'HG00612', 'HG00613', 'HG00614', 'HG00615',
                   'HG00619', 'HG00620', 'HG00621', 'HG00622', 'HG00623', 'HG00624', 'HG00625', 'HG00626', 'HG00627',
                   'HG00628', 'HG00629', 'HG00630', 'HG00631', 'HG00632', 'HG00633', 'HG00634', 'HG00635', 'HG00636',
                   'HG00650', 'HG00651', 'HG00652', 'HG00653', 'HG00654', 'HG00655', 'HG00656', 'HG00657', 'HG00658',
                   'HG00662', 'HG00663', 'HG00664', 'HG00671', 'HG00672', 'HG00673', 'HG00674', 'HG00675', 'HG00676',
                   'HG00683', 'HG00684', 'HG00685', 'HG00689', 'HG00690', 'HG00691', 'HG00692', 'HG00693', 'HG00694',
                   'HG00698', 'HG00699', 'HG00700', 'HG00701', 'HG00702', 'HG00703', 'HG00704', 'HG00705', 'HG00706',
                   'HG00707', 'HG00708', 'HG00709', 'HG00716', 'HG00717', 'HG00718', 'HG00728', 'HG00729', 'HG00730'],
           'gih': ['NA20845', 'NA20846', 'NA20847', 'NA20849', 'NA20850', 'NA20851', 'NA20852', 'NA20853', 'NA20854',
                   'NA20856', 'NA20858', 'NA20859', 'NA20861', 'NA20862', 'NA20863', 'NA20864', 'NA20866', 'NA20867',
                   'NA20868', 'NA20869', 'NA20870', 'NA20871', 'NA20872', 'NA20873', 'NA20874', 'NA20875', 'NA20876',
                   'NA20877', 'NA20878', 'NA20879', 'NA20881', 'NA20882', 'NA20883', 'NA20884', 'NA20885', 'NA20886',
                   'NA20887', 'NA20888', 'NA20889', 'NA20890', 'NA20891', 'NA20892', 'NA20893', 'NA20894', 'NA20895',
                   'NA20896', 'NA20897', 'NA20898', 'NA20899', 'NA20900', 'NA20901', 'NA20902', 'NA20903', 'NA20904',
                   'NA20905', 'NA20906', 'NA20907', 'NA20908', 'NA20909', 'NA20910', 'NA20911', 'NA21086', 'NA21087',
                   'NA21088', 'NA21089', 'NA21090', 'NA21091', 'NA21092', 'NA21093', 'NA21094', 'NA21095', 'NA21097',
                   'NA21098', 'NA21099', 'NA21100', 'NA21101', 'NA21102', 'NA21103', 'NA21104', 'NA21105', 'NA21106',
                   'NA21107', 'NA21108', 'NA21109', 'NA21110', 'NA21111', 'NA21112', 'NA21113', 'NA21114', 'NA21115',
                   'NA21116', 'NA21117', 'NA21118', 'NA21119', 'NA21120', 'NA21121', 'NA21122', 'NA21123', 'NA21124',
                   'NA21125', 'NA21126', 'NA21127', 'NA21128', 'NA21129', 'NA21130', 'NA21133', 'NA21134', 'NA21135',
                   'NA21137', 'NA21141', 'NA21142', 'NA21143', 'NA21144'],
           'lwk': ['NA19017', 'NA19019', 'NA19020', 'NA19023', 'NA19024', 'NA19025', 'NA19026', 'NA19027', 'NA19028',
                   'NA19030', 'NA19031', 'NA19035', 'NA19036', 'NA19037', 'NA19038', 'NA19041', 'NA19042', 'NA19043',
                   'NA19044', 'NA19046', 'NA19307', 'NA19308', 'NA19309', 'NA19310', 'NA19311', 'NA19312', 'NA19313',
                   'NA19314', 'NA19315', 'NA19316', 'NA19317', 'NA19318', 'NA19319', 'NA19320', 'NA19321', 'NA19323',
                   'NA19324', 'NA19327', 'NA19328', 'NA19331', 'NA19332', 'NA19334', 'NA19338', 'NA19346', 'NA19347',
                   'NA19350', 'NA19351', 'NA19352', 'NA19355', 'NA19359', 'NA19360', 'NA19371', 'NA19372', 'NA19373',
                   'NA19374', 'NA19375', 'NA19376', 'NA19377', 'NA19378', 'NA19379', 'NA19380', 'NA19381', 'NA19382',
                   'NA19383', 'NA19384', 'NA19385', 'NA19390', 'NA19391', 'NA19393', 'NA19394', 'NA19395', 'NA19396',
                   'NA19397', 'NA19398', 'NA19399', 'NA19401', 'NA19403', 'NA19404', 'NA19428', 'NA19429', 'NA19430',
                   'NA19431', 'NA19432', 'NA19434', 'NA19435', 'NA19436', 'NA19437', 'NA19438', 'NA19439', 'NA19440',
                   'NA19443', 'NA19444', 'NA19445', 'NA19446', 'NA19448', 'NA19449', 'NA19451', 'NA19452', 'NA19453',
                   'NA19454', 'NA19455', 'NA19456', 'NA19457', 'NA19461', 'NA19462', 'NA19463', 'NA19466', 'NA19467',
                   'NA19468', 'NA19469', 'NA19470', 'NA19471', 'NA19472', 'NA19473', 'NA19474', 'NA19475'],
           'asw': ['NA19625', 'NA19700', 'NA19701', 'NA19702', 'NA19703', 'NA19704', 'NA19705', 'NA19707', 'NA19708',
                   'NA19711', 'NA19712', 'NA19713', 'NA19714', 'NA19818', 'NA19819', 'NA19828', 'NA19834', 'NA19835',
                   'NA19836', 'NA19900', 'NA19901', 'NA19902', 'NA19904', 'NA19905', 'NA19908', 'NA19909', 'NA19913',
                   'NA19914', 'NA19915', 'NA19916', 'NA19917', 'NA19918', 'NA19919', 'NA19920', 'NA19921', 'NA19922',
                   'NA19923', 'NA19924', 'NA19982', 'NA19983', 'NA19984', 'NA19985', 'NA20126', 'NA20127', 'NA20128',
                   'NA20129', 'NA20274', 'NA20276', 'NA20277', 'NA20278', 'NA20279', 'NA20281', 'NA20282', 'NA20284',
                   'NA20285', 'NA20287', 'NA20288', 'NA20289', 'NA20290', 'NA20291', 'NA20292', 'NA20294', 'NA20295',
                   'NA20296', 'NA20297', 'NA20298', 'NA20299', 'NA20300', 'NA20301', 'NA20302', 'NA20312', 'NA20313',
                   'NA20314', 'NA20316', 'NA20317', 'NA20318', 'NA20319', 'NA20320', 'NA20321', 'NA20322', 'NA20332',
                   'NA20333', 'NA20334', 'NA20335', 'NA20336', 'NA20337', 'NA20339', 'NA20340', 'NA20341', 'NA20342',
                   'NA20343', 'NA20344', 'NA20345', 'NA20346', 'NA20347', 'NA20348', 'NA20349', 'NA20350', 'NA20351',
                   'NA20355', 'NA20356', 'NA20357', 'NA20358', 'NA20359', 'NA20360', 'NA20361', 'NA20362', 'NA20363',
                   'NA20364', 'NA20412', 'NA20413', 'NA20414'],
           'clm': ['HG01112', 'HG01113', 'HG01114', 'HG01119', 'HG01121', 'HG01122', 'HG01123', 'HG01124', 'HG01125',
                   'HG01126', 'HG01130', 'HG01131', 'HG01133', 'HG01134', 'HG01135', 'HG01136', 'HG01137', 'HG01138',
                   'HG01139', 'HG01140', 'HG01141', 'HG01142', 'HG01148', 'HG01149', 'HG01150', 'HG01250', 'HG01251',
                   'HG01252', 'HG01253', 'HG01254', 'HG01255', 'HG01256', 'HG01257', 'HG01258', 'HG01259', 'HG01260',
                   'HG01261', 'HG01269', 'HG01271', 'HG01272', 'HG01273', 'HG01274', 'HG01275', 'HG01276', 'HG01277',
                   'HG01278', 'HG01279', 'HG01280', 'HG01281', 'HG01284', 'HG01341', 'HG01342', 'HG01343', 'HG01344',
                   'HG01345', 'HG01346', 'HG01347', 'HG01348', 'HG01349', 'HG01350', 'HG01351', 'HG01352', 'HG01353',
                   'HG01354', 'HG01355', 'HG01356', 'HG01357', 'HG01358', 'HG01359', 'HG01360', 'HG01361', 'HG01362',
                   'HG01363', 'HG01364', 'HG01365', 'HG01366', 'HG01367', 'HG01369', 'HG01372', 'HG01374', 'HG01375',
                   'HG01376', 'HG01377', 'HG01378', 'HG01379', 'HG01383', 'HG01384', 'HG01385', 'HG01389', 'HG01390',
                   'HG01391', 'HG01431', 'HG01432', 'HG01433', 'HG01435', 'HG01437', 'HG01438', 'HG01439', 'HG01440',
                   'HG01441', 'HG01442', 'HG01443', 'HG01444', 'HG01445', 'HG01447', 'HG01452', 'HG01453', 'HG01454',
                   'HG01455', 'HG01456', 'HG01457', 'HG01459', 'HG01461', 'HG01462', 'HG01463', 'HG01464', 'HG01465',
                   'HG01466', 'HG01468', 'HG01471', 'HG01473', 'HG01474', 'HG01477', 'HG01479', 'HG01480', 'HG01481',
                   'HG01482', 'HG01483', 'HG01484', 'HG01485', 'HG01486', 'HG01487', 'HG01488', 'HG01489', 'HG01490',
                   'HG01491', 'HG01492', 'HG01493', 'HG01494', 'HG01495', 'HG01496', 'HG01497', 'HG01498', 'HG01499',
                   'HG01550', 'HG01551', 'HG01552', 'HG01556'],
           'gwd': ['HG02461', 'HG02462', 'HG02463', 'HG02464', 'HG02465', 'HG02466', 'HG02561', 'HG02562', 'HG02563',
                   'HG02567', 'HG02568', 'HG02569', 'HG02570', 'HG02571', 'HG02572', 'HG02573', 'HG02574', 'HG02575',
                   'HG02582', 'HG02583', 'HG02584', 'HG02585', 'HG02586', 'HG02587', 'HG02588', 'HG02589', 'HG02590',
                   'HG02594', 'HG02595', 'HG02596', 'HG02610', 'HG02611', 'HG02612', 'HG02613', 'HG02614', 'HG02615',
                   'HG02620', 'HG02621', 'HG02622', 'HG02623', 'HG02624', 'HG02625', 'HG02628', 'HG02629', 'HG02630',
                   'HG02634', 'HG02635', 'HG02636', 'HG02642', 'HG02643', 'HG02644', 'HG02645', 'HG02646', 'HG02647',
                   'HG02666', 'HG02667', 'HG02668', 'HG02675', 'HG02676', 'HG02677', 'HG02678', 'HG02679', 'HG02680',
                   'HG02702', 'HG02703', 'HG02704', 'HG02715', 'HG02716', 'HG02717', 'HG02721', 'HG02722', 'HG02723',
                   'HG02756', 'HG02757', 'HG02758', 'HG02759', 'HG02760', 'HG02761', 'HG02762', 'HG02763', 'HG02764',
                   'HG02768', 'HG02769', 'HG02770', 'HG02771', 'HG02772', 'HG02773', 'HG02798', 'HG02799', 'HG02800',
                   'HG02804', 'HG02805', 'HG02806', 'HG02807', 'HG02808', 'HG02809', 'HG02810', 'HG02811', 'HG02812',
                   'HG02813', 'HG02814', 'HG02815', 'HG02816', 'HG02817', 'HG02818', 'HG02819', 'HG02820', 'HG02821',
                   'HG02836', 'HG02837', 'HG02838', 'HG02839', 'HG02840', 'HG02841', 'HG02851', 'HG02852', 'HG02853',
                   'HG02854', 'HG02855', 'HG02856', 'HG02860', 'HG02861', 'HG02862', 'HG02869', 'HG02870', 'HG02871',
                   'HG02878', 'HG02879', 'HG02880', 'HG02881', 'HG02882', 'HG02883', 'HG02884', 'HG02885', 'HG02886',
                   'HG02887', 'HG02888', 'HG02889', 'HG02890', 'HG02891', 'HG02892', 'HG02895', 'HG02896', 'HG02897',
                   'HG02982', 'HG02983', 'HG02984', 'HG03024', 'HG03025', 'HG03026', 'HG03027', 'HG03028', 'HG03029',
                   'HG03033', 'HG03034', 'HG03035', 'HG03039', 'HG03040', 'HG03041', 'HG03045', 'HG03046', 'HG03047',
                   'HG03048', 'HG03049', 'HG03050', 'HG03240', 'HG03241', 'HG03242', 'HG03246', 'HG03247', 'HG03248',
                   'HG03249', 'HG03250', 'HG03251', 'HG03258', 'HG03259', 'HG03260', 'HG03538', 'HG03539', 'HG03540'],
           'msl': ['HG03052', 'HG03053', 'HG03054', 'HG03055', 'HG03056', 'HG03057', 'HG03058', 'HG03059', 'HG03060',
                   'HG03061', 'HG03062', 'HG03063', 'HG03064', 'HG03065', 'HG03066', 'HG03069', 'HG03072', 'HG03073',
                   'HG03074', 'HG03076', 'HG03077', 'HG03078', 'HG03079', 'HG03080', 'HG03081', 'HG03082', 'HG03084',
                   'HG03085', 'HG03086', 'HG03088', 'HG03091', 'HG03095', 'HG03096', 'HG03097', 'HG03098', 'HG03209',
                   'HG03212', 'HG03224', 'HG03225', 'HG03376', 'HG03378', 'HG03380', 'HG03381', 'HG03382', 'HG03383',
                   'HG03384', 'HG03385', 'HG03388', 'HG03390', 'HG03391', 'HG03393', 'HG03394', 'HG03397', 'HG03398',
                   'HG03399', 'HG03401', 'HG03402', 'HG03408', 'HG03410', 'HG03411', 'HG03419', 'HG03428', 'HG03431',
                   'HG03432', 'HG03433', 'HG03436', 'HG03437', 'HG03438', 'HG03439', 'HG03442', 'HG03445', 'HG03446',
                   'HG03449', 'HG03450', 'HG03451', 'HG03452', 'HG03453', 'HG03454', 'HG03455', 'HG03456', 'HG03457',
                   'HG03458', 'HG03459', 'HG03460', 'HG03461', 'HG03462', 'HG03464', 'HG03465', 'HG03466', 'HG03468',
                   'HG03469', 'HG03470', 'HG03471', 'HG03472', 'HG03473', 'HG03474', 'HG03476', 'HG03477', 'HG03478',
                   'HG03479', 'HG03480', 'HG03484', 'HG03485', 'HG03486', 'HG03547', 'HG03548', 'HG03549', 'HG03556',
                   'HG03557', 'HG03558', 'HG03559', 'HG03563', 'HG03564', 'HG03565', 'HG03566', 'HG03567', 'HG03569',
                   'HG03571', 'HG03572', 'HG03574', 'HG03575', 'HG03576', 'HG03577', 'HG03578', 'HG03579', 'HG03582',
                   'HG03583', 'HG03584'],
           'pur': ['HG00551', 'HG00552', 'HG00553', 'HG00554', 'HG00555', 'HG00637', 'HG00638', 'HG00639', 'HG00640',
                   'HG00641', 'HG00642', 'HG00731', 'HG00732', 'HG00733', 'HG00734', 'HG00735', 'HG00736', 'HG00737',
                   'HG00738', 'HG00739', 'HG00740', 'HG00741', 'HG00742', 'HG00743', 'HG01047', 'HG01048', 'HG01049',
                   'HG01050', 'HG01051', 'HG01052', 'HG01053', 'HG01054', 'HG01055', 'HG01056', 'HG01058', 'HG01060',
                   'HG01061', 'HG01062', 'HG01063', 'HG01064', 'HG01066', 'HG01067', 'HG01068', 'HG01069', 'HG01070',
                   'HG01071', 'HG01072', 'HG01073', 'HG01074', 'HG01075', 'HG01077', 'HG01079', 'HG01080', 'HG01081',
                   'HG01082', 'HG01083', 'HG01084', 'HG01085', 'HG01086', 'HG01087', 'HG01088', 'HG01089', 'HG01090',
                   'HG01092', 'HG01094', 'HG01095', 'HG01096', 'HG01097', 'HG01098', 'HG01099', 'HG01100', 'HG01101',
                   'HG01102', 'HG01103', 'HG01104', 'HG01105', 'HG01106', 'HG01107', 'HG01108', 'HG01109', 'HG01110',
                   'HG01111', 'HG01161', 'HG01162', 'HG01164', 'HG01167', 'HG01168', 'HG01169', 'HG01170', 'HG01171',
                   'HG01172', 'HG01173', 'HG01174', 'HG01175', 'HG01176', 'HG01177', 'HG01178', 'HG01182', 'HG01183',
                   'HG01184', 'HG01187', 'HG01188', 'HG01189', 'HG01190', 'HG01191', 'HG01192', 'HG01195', 'HG01197',
                   'HG01198', 'HG01199', 'HG01200', 'HG01204', 'HG01205', 'HG01206', 'HG01241', 'HG01242', 'HG01243',
                   'HG01247', 'HG01248', 'HG01249', 'HG01286', 'HG01301', 'HG01302', 'HG01303', 'HG01305', 'HG01308',
                   'HG01311', 'HG01312', 'HG01322', 'HG01323', 'HG01324', 'HG01325', 'HG01326', 'HG01327', 'HG01392',
                   'HG01393', 'HG01394', 'HG01395', 'HG01396', 'HG01397', 'HG01398', 'HG01402', 'HG01403', 'HG01404',
                   'HG01405', 'HG01411', 'HG01412', 'HG01413', 'HG01414', 'HG01415'],
           'beb': ['HG03006', 'HG03007', 'HG03008', 'HG03009', 'HG03012', 'HG03585', 'HG03587', 'HG03589', 'HG03590',
                   'HG03593', 'HG03594', 'HG03595', 'HG03596', 'HG03598', 'HG03599', 'HG03600', 'HG03602', 'HG03603',
                   'HG03604', 'HG03605', 'HG03606', 'HG03607', 'HG03611', 'HG03615', 'HG03616', 'HG03617', 'HG03793',
                   'HG03794', 'HG03795', 'HG03796', 'HG03797', 'HG03798', 'HG03799', 'HG03800', 'HG03801', 'HG03802',
                   'HG03803', 'HG03804', 'HG03805', 'HG03806', 'HG03807', 'HG03808', 'HG03809', 'HG03811', 'HG03812',
                   'HG03813', 'HG03814', 'HG03815', 'HG03816', 'HG03817', 'HG03821', 'HG03822', 'HG03823', 'HG03824',
                   'HG03825', 'HG03826', 'HG03829', 'HG03830', 'HG03831', 'HG03832', 'HG03833', 'HG03834', 'HG03901',
                   'HG03902', 'HG03903', 'HG03904', 'HG03905', 'HG03906', 'HG03907', 'HG03908', 'HG03909', 'HG03910',
                   'HG03911', 'HG03913', 'HG03914', 'HG03915', 'HG03916', 'HG03917', 'HG03919', 'HG03920', 'HG03922',
                   'HG03924', 'HG03925', 'HG03926', 'HG03927', 'HG03928', 'HG03929', 'HG03930', 'HG03931', 'HG03934',
                   'HG03937', 'HG03939', 'HG03940', 'HG03941', 'HG03942', 'HG04128', 'HG04131', 'HG04132', 'HG04133',
                   'HG04134', 'HG04135', 'HG04136', 'HG04140', 'HG04141', 'HG04142', 'HG04144', 'HG04146', 'HG04147',
                   'HG04148', 'HG04149', 'HG04150', 'HG04151', 'HG04152', 'HG04153', 'HG04155', 'HG04156', 'HG04157',
                   'HG04158', 'HG04159', 'HG04160', 'HG04161', 'HG04162', 'HG04164', 'HG04171', 'HG04173', 'HG04174',
                   'HG04175', 'HG04176', 'HG04177', 'HG04180', 'HG04181', 'HG04182', 'HG04183', 'HG04184', 'HG04185',
                   'HG04186', 'HG04187', 'HG04188', 'HG04189', 'HG04191', 'HG04192', 'HG04193', 'HG04194', 'HG04195'],
           'mxl': ['NA19648', 'NA19649', 'NA19650', 'NA19651', 'NA19652', 'NA19653', 'NA19654', 'NA19655', 'NA19656',
                   'NA19657', 'NA19658', 'NA19659', 'NA19660', 'NA19661', 'NA19662', 'NA19663', 'NA19664', 'NA19665',
                   'NA19669', 'NA19670', 'NA19671', 'NA19672', 'NA19674', 'NA19675', 'NA19676', 'NA19677', 'NA19678',
                   'NA19679', 'NA19680', 'NA19681', 'NA19682', 'NA19683', 'NA19684', 'NA19685', 'NA19686', 'NA19716',
                   'NA19717', 'NA19718', 'NA19719', 'NA19720', 'NA19721', 'NA19722', 'NA19723', 'NA19724', 'NA19725',
                   'NA19726', 'NA19727', 'NA19728', 'NA19729', 'NA19730', 'NA19731', 'NA19732', 'NA19733', 'NA19734',
                   'NA19735', 'NA19737', 'NA19738', 'NA19740', 'NA19741', 'NA19742', 'NA19746', 'NA19747', 'NA19748',
                   'NA19749', 'NA19750', 'NA19751', 'NA19752', 'NA19753', 'NA19754', 'NA19755', 'NA19756', 'NA19757',
                   'NA19758', 'NA19759', 'NA19760', 'NA19761', 'NA19762', 'NA19763', 'NA19764', 'NA19766', 'NA19770',
                   'NA19771', 'NA19772', 'NA19773', 'NA19774', 'NA19775', 'NA19776', 'NA19777', 'NA19778', 'NA19779',
                   'NA19780', 'NA19781', 'NA19782', 'NA19783', 'NA19784', 'NA19785', 'NA19786', 'NA19787', 'NA19788',
                   'NA19789', 'NA19790', 'NA19792', 'NA19794', 'NA19795', 'NA19796', 'NA19797', 'NA19798'],
           'stu': ['HG03642', 'HG03643', 'HG03644', 'HG03645', 'HG03646', 'HG03672', 'HG03673', 'HG03679', 'HG03680',
                   'HG03681', 'HG03682', 'HG03683', 'HG03684', 'HG03685', 'HG03686', 'HG03687', 'HG03688', 'HG03689',
                   'HG03690', 'HG03691', 'HG03692', 'HG03693', 'HG03694', 'HG03695', 'HG03696', 'HG03697', 'HG03698',
                   'HG03711', 'HG03733', 'HG03736', 'HG03738', 'HG03740', 'HG03741', 'HG03743', 'HG03744', 'HG03745',
                   'HG03746', 'HG03750', 'HG03752', 'HG03753', 'HG03754', 'HG03755', 'HG03756', 'HG03757', 'HG03760',
                   'HG03835', 'HG03836', 'HG03837', 'HG03838', 'HG03840', 'HG03842', 'HG03844', 'HG03845', 'HG03846',
                   'HG03847', 'HG03848', 'HG03849', 'HG03850', 'HG03851', 'HG03854', 'HG03856', 'HG03857', 'HG03858',
                   'HG03884', 'HG03885', 'HG03886', 'HG03887', 'HG03888', 'HG03890', 'HG03894', 'HG03895', 'HG03896',
                   'HG03897', 'HG03898', 'HG03899', 'HG03900', 'HG03943', 'HG03944', 'HG03945', 'HG03947', 'HG03948',
                   'HG03949', 'HG03950', 'HG03951', 'HG03953', 'HG03955', 'HG03982', 'HG03985', 'HG03986', 'HG03988',
                   'HG03989', 'HG03990', 'HG03991', 'HG03992', 'HG03995', 'HG03998', 'HG03999', 'HG04003', 'HG04006',
                   'HG04029', 'HG04033', 'HG04035', 'HG04036', 'HG04037', 'HG04038', 'HG04039', 'HG04040', 'HG04042',
                   'HG04047', 'HG04067', 'HG04075', 'HG04099', 'HG04100', 'HG04106', 'HG04107', 'HG04114', 'HG04115',
                   'HG04122', 'HG04127', 'HG04197', 'HG04199', 'HG04204', 'HG04208', 'HG04210', 'HG04215', 'HG04227',
                   'HG04228', 'HG04229'],
           'cdx': ['HG00759', 'HG00766', 'HG00844', 'HG00851', 'HG00864', 'HG00866', 'HG00867', 'HG00879', 'HG00881',
                   'HG00956', 'HG00978', 'HG00982', 'HG00983', 'HG01028', 'HG01029', 'HG01031', 'HG01046', 'HG01794',
                   'HG01795', 'HG01796', 'HG01797', 'HG01798', 'HG01799', 'HG01800', 'HG01801', 'HG01802', 'HG01804',
                   'HG01805', 'HG01806', 'HG01807', 'HG01808', 'HG01809', 'HG01810', 'HG01811', 'HG01812', 'HG01813',
                   'HG01815', 'HG01816', 'HG01817', 'HG02151', 'HG02152', 'HG02153', 'HG02154', 'HG02155', 'HG02156',
                   'HG02164', 'HG02165', 'HG02166', 'HG02168', 'HG02169', 'HG02170', 'HG02173', 'HG02176', 'HG02178',
                   'HG02179', 'HG02180', 'HG02181', 'HG02182', 'HG02184', 'HG02185', 'HG02186', 'HG02187', 'HG02188',
                   'HG02189', 'HG02190', 'HG02250', 'HG02351', 'HG02353', 'HG02355', 'HG02356', 'HG02358', 'HG02360',
                   'HG02363', 'HG02364', 'HG02367', 'HG02371', 'HG02372', 'HG02373', 'HG02374', 'HG02375', 'HG02377',
                   'HG02379', 'HG02380', 'HG02381', 'HG02382', 'HG02383', 'HG02384', 'HG02385', 'HG02386', 'HG02387',
                   'HG02388', 'HG02389', 'HG02390', 'HG02391', 'HG02392', 'HG02394', 'HG02395', 'HG02396', 'HG02397',
                   'HG02398', 'HG02399', 'HG02401', 'HG02402', 'HG02405', 'HG02406', 'HG02407', 'HG02408', 'HG02409',
                   'HG02410'],
           'esn': ['HG02922', 'HG02923', 'HG02924', 'HG02938', 'HG02939', 'HG02941', 'HG02942', 'HG02943', 'HG02944',
                   'HG02945', 'HG02946', 'HG02947', 'HG02948', 'HG02952', 'HG02953', 'HG02954', 'HG02964', 'HG02965',
                   'HG02966', 'HG02968', 'HG02969', 'HG02970', 'HG02971', 'HG02972', 'HG02973', 'HG02974', 'HG02975',
                   'HG02976', 'HG02977', 'HG02978', 'HG02979', 'HG02980', 'HG02981', 'HG03099', 'HG03100', 'HG03101',
                   'HG03103', 'HG03104', 'HG03105', 'HG03107', 'HG03108', 'HG03109', 'HG03110', 'HG03111', 'HG03112',
                   'HG03113', 'HG03114', 'HG03115', 'HG03116', 'HG03117', 'HG03118', 'HG03119', 'HG03120', 'HG03121',
                   'HG03122', 'HG03123', 'HG03124', 'HG03125', 'HG03126', 'HG03127', 'HG03128', 'HG03129', 'HG03130',
                   'HG03131', 'HG03132', 'HG03133', 'HG03134', 'HG03135', 'HG03136', 'HG03137', 'HG03139', 'HG03140',
                   'HG03157', 'HG03158', 'HG03159', 'HG03160', 'HG03161', 'HG03162', 'HG03163', 'HG03164', 'HG03166',
                   'HG03167', 'HG03168', 'HG03169', 'HG03170', 'HG03171', 'HG03172', 'HG03173', 'HG03175', 'HG03176',
                   'HG03189', 'HG03190', 'HG03191', 'HG03193', 'HG03194', 'HG03195', 'HG03196', 'HG03197', 'HG03198',
                   'HG03199', 'HG03200', 'HG03202', 'HG03203', 'HG03265', 'HG03266', 'HG03267', 'HG03268', 'HG03269',
                   'HG03270', 'HG03271', 'HG03272', 'HG03279', 'HG03280', 'HG03291', 'HG03293', 'HG03294', 'HG03295',
                   'HG03296', 'HG03297', 'HG03298', 'HG03299', 'HG03300', 'HG03301', 'HG03302', 'HG03303', 'HG03304',
                   'HG03305', 'HG03306', 'HG03307', 'HG03308', 'HG03309', 'HG03310', 'HG03311', 'HG03312', 'HG03313',
                   'HG03314', 'HG03339', 'HG03341', 'HG03342', 'HG03343', 'HG03344', 'HG03350', 'HG03351', 'HG03352',
                   'HG03354', 'HG03361', 'HG03362', 'HG03363', 'HG03365', 'HG03366', 'HG03367', 'HG03368', 'HG03369',
                   'HG03370', 'HG03371', 'HG03372', 'HG03373', 'HG03374', 'HG03493', 'HG03499', 'HG03508', 'HG03510',
                   'HG03511', 'HG03513', 'HG03514', 'HG03515', 'HG03516', 'HG03517', 'HG03518', 'HG03519', 'HG03520',
                   'HG03521', 'HG03522'],
           'itu': ['HG03713', 'HG03714', 'HG03715', 'HG03716', 'HG03717', 'HG03718', 'HG03719', 'HG03720', 'HG03721',
                   'HG03722', 'HG03723', 'HG03725', 'HG03727', 'HG03729', 'HG03730', 'HG03731', 'HG03732', 'HG03742',
                   'HG03770', 'HG03771', 'HG03772', 'HG03773', 'HG03774', 'HG03775', 'HG03777', 'HG03778', 'HG03779',
                   'HG03780', 'HG03781', 'HG03782', 'HG03783', 'HG03784', 'HG03785', 'HG03786', 'HG03787', 'HG03788',
                   'HG03789', 'HG03790', 'HG03792', 'HG03861', 'HG03862', 'HG03863', 'HG03864', 'HG03866', 'HG03867',
                   'HG03868', 'HG03869', 'HG03870', 'HG03871', 'HG03872', 'HG03873', 'HG03874', 'HG03875', 'HG03876',
                   'HG03879', 'HG03882', 'HG03960', 'HG03963', 'HG03965', 'HG03967', 'HG03968', 'HG03969', 'HG03971',
                   'HG03972', 'HG03973', 'HG03974', 'HG03976', 'HG03977', 'HG03978', 'HG04001', 'HG04002', 'HG04014',
                   'HG04015', 'HG04017', 'HG04018', 'HG04019', 'HG04020', 'HG04022', 'HG04023', 'HG04024', 'HG04025',
                   'HG04026', 'HG04050', 'HG04053', 'HG04054', 'HG04055', 'HG04056', 'HG04058', 'HG04059', 'HG04060',
                   'HG04061', 'HG04062', 'HG04063', 'HG04070', 'HG04076', 'HG04080', 'HG04090', 'HG04093', 'HG04094',
                   'HG04096', 'HG04098', 'HG04118', 'HG04198', 'HG04200', 'HG04202', 'HG04206', 'HG04209', 'HG04211',
                   'HG04212', 'HG04214', 'HG04216', 'HG04217', 'HG04219', 'HG04222', 'HG04225', 'HG04235', 'HG04238',
                   'HG04239'],
           'tsi': ['NA20502', 'NA20503', 'NA20504', 'NA20505', 'NA20506', 'NA20507', 'NA20508', 'NA20509', 'NA20510',
                   'NA20511', 'NA20512', 'NA20513', 'NA20514', 'NA20515', 'NA20516', 'NA20517', 'NA20518', 'NA20519',
                   'NA20520', 'NA20521', 'NA20522', 'NA20524', 'NA20525', 'NA20526', 'NA20527', 'NA20528', 'NA20529',
                   'NA20530', 'NA20531', 'NA20532', 'NA20533', 'NA20534', 'NA20535', 'NA20536', 'NA20537', 'NA20538',
                   'NA20539', 'NA20540', 'NA20541', 'NA20542', 'NA20543', 'NA20544', 'NA20581', 'NA20582', 'NA20585',
                   'NA20586', 'NA20587', 'NA20588', 'NA20589', 'NA20752', 'NA20753', 'NA20754', 'NA20755', 'NA20756',
                   'NA20757', 'NA20758', 'NA20759', 'NA20760', 'NA20761', 'NA20762', 'NA20763', 'NA20764', 'NA20765',
                   'NA20766', 'NA20767', 'NA20768', 'NA20769', 'NA20770', 'NA20771', 'NA20772', 'NA20773', 'NA20774',
                   'NA20775', 'NA20778', 'NA20783', 'NA20785', 'NA20786', 'NA20787', 'NA20790', 'NA20792', 'NA20795',
                   'NA20796', 'NA20797', 'NA20798', 'NA20799', 'NA20800', 'NA20801', 'NA20802', 'NA20803', 'NA20804',
                   'NA20805', 'NA20806', 'NA20807', 'NA20808', 'NA20809', 'NA20810', 'NA20811', 'NA20812', 'NA20813',
                   'NA20814', 'NA20815', 'NA20816', 'NA20818', 'NA20819', 'NA20821', 'NA20822', 'NA20826', 'NA20827',
                   'NA20828', 'NA20829', 'NA20831', 'NA20832'],
           'ceu': ['NA06984', 'NA06985', 'NA06986', 'NA06989', 'NA06991', 'NA06993', 'NA06994', 'NA06995', 'NA06997',
                   'NA07000', 'NA07014', 'NA07019', 'NA07022', 'NA07029', 'NA07031', 'NA07034', 'NA07037', 'NA07045',
                   'NA07048', 'NA07051', 'NA07055', 'NA07056', 'NA07340', 'NA07345', 'NA07346', 'NA07347', 'NA07348',
                   'NA07349', 'NA07357', 'NA07435', 'NA10830', 'NA10831', 'NA10835', 'NA10836', 'NA10837', 'NA10838',
                   'NA10839', 'NA10840', 'NA10842', 'NA10843', 'NA10845', 'NA10846', 'NA10847', 'NA10850', 'NA10851',
                   'NA10852', 'NA10853', 'NA10854', 'NA10855', 'NA10856', 'NA10857', 'NA10859', 'NA10860', 'NA10861',
                   'NA10863', 'NA10864', 'NA10865', 'NA11829', 'NA11830', 'NA11831', 'NA11832', 'NA11839', 'NA11840',
                   'NA11843', 'NA11881', 'NA11882', 'NA11891', 'NA11892', 'NA11893', 'NA11894', 'NA11917', 'NA11918',
                   'NA11919', 'NA11920', 'NA11930', 'NA11931', 'NA11932', 'NA11933', 'NA11992', 'NA11993', 'NA11994',
                   'NA11995', 'NA12003', 'NA12004', 'NA12005', 'NA12006', 'NA12043', 'NA12044', 'NA12045', 'NA12046',
                   'NA12056', 'NA12057', 'NA12058', 'NA12144', 'NA12145', 'NA12146', 'NA12154', 'NA12155', 'NA12156',
                   'NA12234', 'NA12239', 'NA12248', 'NA12249', 'NA12264', 'NA12272', 'NA12273', 'NA12274', 'NA12275',
                   'NA12282', 'NA12283', 'NA12286', 'NA12287', 'NA12329', 'NA12335', 'NA12336', 'NA12340', 'NA12341',
                   'NA12342', 'NA12343', 'NA12344', 'NA12347', 'NA12348', 'NA12375', 'NA12376', 'NA12383', 'NA12386',
                   'NA12399', 'NA12400', 'NA12413', 'NA12414', 'NA12485', 'NA12489', 'NA12546', 'NA12707', 'NA12708',
                   'NA12716', 'NA12717', 'NA12718', 'NA12739', 'NA12740', 'NA12748', 'NA12749', 'NA12750', 'NA12751',
                   'NA12752', 'NA12753', 'NA12760', 'NA12761', 'NA12762', 'NA12763', 'NA12766', 'NA12767', 'NA12775',
                   'NA12776', 'NA12777', 'NA12778', 'NA12801', 'NA12802', 'NA12812', 'NA12813', 'NA12814', 'NA12815',
                   'NA12817', 'NA12818', 'NA12827', 'NA12828', 'NA12829', 'NA12830', 'NA12832', 'NA12842', 'NA12843',
                   'NA12864', 'NA12865', 'NA12872', 'NA12873', 'NA12874', 'NA12875', 'NA12877', 'NA12878', 'NA12889',
                   'NA12890', 'NA12891', 'NA12892'],
           'fin': ['HG00171', 'HG00173', 'HG00174', 'HG00176', 'HG00177', 'HG00178', 'HG00179', 'HG00180', 'HG00181',
                   'HG00182', 'HG00183', 'HG00185', 'HG00186', 'HG00187', 'HG00188', 'HG00189', 'HG00190', 'HG00266',
                   'HG00267', 'HG00268', 'HG00269', 'HG00270', 'HG00271', 'HG00272', 'HG00273', 'HG00274', 'HG00275',
                   'HG00276', 'HG00277', 'HG00278', 'HG00280', 'HG00281', 'HG00282', 'HG00284', 'HG00285', 'HG00288',
                   'HG00290', 'HG00302', 'HG00303', 'HG00304', 'HG00306', 'HG00308', 'HG00309', 'HG00310', 'HG00311',
                   'HG00312', 'HG00313', 'HG00315', 'HG00318', 'HG00319', 'HG00320', 'HG00321', 'HG00323', 'HG00324',
                   'HG00325', 'HG00326', 'HG00327', 'HG00328', 'HG00329', 'HG00330', 'HG00331', 'HG00332', 'HG00334',
                   'HG00335', 'HG00336', 'HG00337', 'HG00338', 'HG00339', 'HG00341', 'HG00342', 'HG00343', 'HG00344',
                   'HG00345', 'HG00346', 'HG00349', 'HG00350', 'HG00351', 'HG00353', 'HG00355', 'HG00356', 'HG00357',
                   'HG00358', 'HG00359', 'HG00360', 'HG00361', 'HG00362', 'HG00364', 'HG00365', 'HG00366', 'HG00367',
                   'HG00368', 'HG00369', 'HG00371', 'HG00372', 'HG00373', 'HG00375', 'HG00376', 'HG00377', 'HG00378',
                   'HG00379', 'HG00380', 'HG00381', 'HG00382', 'HG00383', 'HG00384'],
           'jpt': ['NA18939', 'NA18940', 'NA18941', 'NA18942', 'NA18943', 'NA18944', 'NA18945', 'NA18946', 'NA18947',
                   'NA18948', 'NA18949', 'NA18950', 'NA18951', 'NA18952', 'NA18953', 'NA18954', 'NA18955', 'NA18956',
                   'NA18957', 'NA18959', 'NA18960', 'NA18961', 'NA18962', 'NA18963', 'NA18964', 'NA18965', 'NA18966',
                   'NA18967', 'NA18968', 'NA18969', 'NA18970', 'NA18971', 'NA18972', 'NA18973', 'NA18974', 'NA18975',
                   'NA18976', 'NA18977', 'NA18978', 'NA18979', 'NA18980', 'NA18981', 'NA18982', 'NA18983', 'NA18984',
                   'NA18985', 'NA18986', 'NA18987', 'NA18988', 'NA18989', 'NA18990', 'NA18991', 'NA18992', 'NA18993',
                   'NA18994', 'NA18995', 'NA18997', 'NA18998', 'NA18999', 'NA19000', 'NA19001', 'NA19002', 'NA19003',
                   'NA19004', 'NA19005', 'NA19006', 'NA19007', 'NA19009', 'NA19010', 'NA19011', 'NA19012', 'NA19054',
                   'NA19055', 'NA19056', 'NA19057', 'NA19058', 'NA19059', 'NA19060', 'NA19062', 'NA19063', 'NA19064',
                   'NA19065', 'NA19066', 'NA19067', 'NA19068', 'NA19070', 'NA19072', 'NA19074', 'NA19075', 'NA19076',
                   'NA19077', 'NA19078', 'NA19079', 'NA19080', 'NA19081', 'NA19082', 'NA19083', 'NA19084', 'NA19085',
                   'NA19086', 'NA19087', 'NA19088', 'NA19089', 'NA19090', 'NA19091'],
           'pel': ['HG01565', 'HG01566', 'HG01567', 'HG01571', 'HG01572', 'HG01573', 'HG01577', 'HG01578', 'HG01579',
                   'HG01892', 'HG01893', 'HG01898', 'HG01917', 'HG01918', 'HG01919', 'HG01920', 'HG01921', 'HG01922',
                   'HG01923', 'HG01924', 'HG01925', 'HG01926', 'HG01927', 'HG01928', 'HG01932', 'HG01933', 'HG01934',
                   'HG01935', 'HG01936', 'HG01937', 'HG01938', 'HG01939', 'HG01940', 'HG01941', 'HG01942', 'HG01943',
                   'HG01944', 'HG01945', 'HG01946', 'HG01947', 'HG01948', 'HG01949', 'HG01950', 'HG01951', 'HG01952',
                   'HG01953', 'HG01954', 'HG01955', 'HG01961', 'HG01965', 'HG01967', 'HG01968', 'HG01969', 'HG01970',
                   'HG01971', 'HG01972', 'HG01973', 'HG01974', 'HG01975', 'HG01976', 'HG01977', 'HG01978', 'HG01979',
                   'HG01980', 'HG01981', 'HG01982', 'HG01983', 'HG01984', 'HG01991', 'HG01992', 'HG01993', 'HG01995',
                   'HG01997', 'HG01998', 'HG02002', 'HG02003', 'HG02004', 'HG02006', 'HG02008', 'HG02089', 'HG02090',
                   'HG02091', 'HG02102', 'HG02104', 'HG02105', 'HG02106', 'HG02146', 'HG02147', 'HG02148', 'HG02150',
                   'HG02252', 'HG02253', 'HG02254', 'HG02259', 'HG02260', 'HG02261', 'HG02262', 'HG02265', 'HG02266',
                   'HG02267', 'HG02271', 'HG02272', 'HG02273', 'HG02274', 'HG02275', 'HG02276', 'HG02277', 'HG02278',
                   'HG02279', 'HG02285', 'HG02286', 'HG02287', 'HG02288', 'HG02291', 'HG02292', 'HG02293', 'HG02298',
                   'HG02299', 'HG02300', 'HG02301', 'HG02302', 'HG02303', 'HG02304', 'HG02312', 'HG02344', 'HG02345',
                   'HG02347', 'HG02348', 'HG02415', 'HG02425'],
           'yri': ['NA18484', 'NA18485', 'NA18486', 'NA18487', 'NA18488', 'NA18489', 'NA18497', 'NA18498', 'NA18499',
                   'NA18500', 'NA18501', 'NA18502', 'NA18503', 'NA18504', 'NA18505', 'NA18506', 'NA18507', 'NA18508',
                   'NA18509', 'NA18510', 'NA18511', 'NA18515', 'NA18516', 'NA18517', 'NA18518', 'NA18519', 'NA18520',
                   'NA18521', 'NA18522', 'NA18523', 'NA18852', 'NA18853', 'NA18854', 'NA18855', 'NA18856', 'NA18857',
                   'NA18858', 'NA18859', 'NA18860', 'NA18861', 'NA18862', 'NA18863', 'NA18864', 'NA18865', 'NA18867',
                   'NA18868', 'NA18869', 'NA18870', 'NA18871', 'NA18872', 'NA18873', 'NA18874', 'NA18875', 'NA18876',
                   'NA18877', 'NA18878', 'NA18879', 'NA18881', 'NA18906', 'NA18907', 'NA18908', 'NA18909', 'NA18910',
                   'NA18911', 'NA18912', 'NA18913', 'NA18914', 'NA18915', 'NA18916', 'NA18917', 'NA18923', 'NA18924',
                   'NA18925', 'NA18930', 'NA18933', 'NA18934', 'NA18935', 'NA19092', 'NA19093', 'NA19094', 'NA19095',
                   'NA19096', 'NA19097', 'NA19098', 'NA19099', 'NA19100', 'NA19101', 'NA19102', 'NA19103', 'NA19104',
                   'NA19105', 'NA19107', 'NA19108', 'NA19109', 'NA19113', 'NA19114', 'NA19115', 'NA19116', 'NA19117',
                   'NA19118', 'NA19119', 'NA19120', 'NA19121', 'NA19122', 'NA19123', 'NA19127', 'NA19128', 'NA19129',
                   'NA19130', 'NA19131', 'NA19132', 'NA19137', 'NA19138', 'NA19139', 'NA19140', 'NA19141', 'NA19142',
                   'NA19143', 'NA19144', 'NA19145', 'NA19146', 'NA19147', 'NA19148', 'NA19149', 'NA19150', 'NA19151',
                   'NA19152', 'NA19153', 'NA19154', 'NA19159', 'NA19160', 'NA19161', 'NA19166', 'NA19171', 'NA19172',
                   'NA19173', 'NA19174', 'NA19175', 'NA19176', 'NA19177', 'NA19184', 'NA19185', 'NA19186', 'NA19189',
                   'NA19190', 'NA19191', 'NA19195', 'NA19196', 'NA19197', 'NA19198', 'NA19199', 'NA19200', 'NA19201',
                   'NA19202', 'NA19203', 'NA19204', 'NA19205', 'NA19206', 'NA19207', 'NA19208', 'NA19209', 'NA19210',
                   'NA19211', 'NA19213', 'NA19214', 'NA19215', 'NA19221', 'NA19222', 'NA19223', 'NA19224', 'NA19225',
                   'NA19226', 'NA19235', 'NA19236', 'NA19237', 'NA19238', 'NA19239', 'NA19240', 'NA19247', 'NA19248',
                   'NA19249', 'NA19252', 'NA19254', 'NA19256', 'NA19257', 'NA19258'],
           'chb': ['NA18525', 'NA18526', 'NA18527', 'NA18528', 'NA18530', 'NA18531', 'NA18532', 'NA18533', 'NA18534',
                   'NA18535', 'NA18536', 'NA18537', 'NA18538', 'NA18539', 'NA18541', 'NA18542', 'NA18543', 'NA18544',
                   'NA18545', 'NA18546', 'NA18547', 'NA18548', 'NA18549', 'NA18550', 'NA18552', 'NA18553', 'NA18555',
                   'NA18557', 'NA18558', 'NA18559', 'NA18560', 'NA18561', 'NA18562', 'NA18563', 'NA18564', 'NA18565',
                   'NA18566', 'NA18567', 'NA18570', 'NA18571', 'NA18572', 'NA18573', 'NA18574', 'NA18576', 'NA18577',
                   'NA18579', 'NA18582', 'NA18591', 'NA18592', 'NA18593', 'NA18595', 'NA18596', 'NA18597', 'NA18599',
                   'NA18602', 'NA18603', 'NA18605', 'NA18606', 'NA18608', 'NA18609', 'NA18610', 'NA18611', 'NA18612',
                   'NA18613', 'NA18614', 'NA18615', 'NA18616', 'NA18617', 'NA18618', 'NA18619', 'NA18620', 'NA18621',
                   'NA18622', 'NA18623', 'NA18624', 'NA18625', 'NA18626', 'NA18627', 'NA18628', 'NA18629', 'NA18630',
                   'NA18631', 'NA18632', 'NA18633', 'NA18634', 'NA18635', 'NA18636', 'NA18637', 'NA18638', 'NA18639',
                   'NA18640', 'NA18641', 'NA18642', 'NA18643', 'NA18644', 'NA18645', 'NA18646', 'NA18647', 'NA18648',
                   'NA18740', 'NA18745', 'NA18747', 'NA18748', 'NA18749', 'NA18757', 'NA18791', 'NA18794', 'NA18795'],
           'gbr': ['HG00096', 'HG00097', 'HG00098', 'HG00099', 'HG00100', 'HG00101', 'HG00102', 'HG00103', 'HG00104',
                   'HG00105', 'HG00106', 'HG00107', 'HG00108', 'HG00109', 'HG00110', 'HG00111', 'HG00112', 'HG00113',
                   'HG00114', 'HG00115', 'HG00116', 'HG00117', 'HG00118', 'HG00119', 'HG00120', 'HG00121', 'HG00122',
                   'HG00123', 'HG00124', 'HG00125', 'HG00126', 'HG00127', 'HG00128', 'HG00129', 'HG00130', 'HG00131',
                   'HG00132', 'HG00133', 'HG00134', 'HG00135', 'HG00136', 'HG00137', 'HG00138', 'HG00139', 'HG00140',
                   'HG00141', 'HG00142', 'HG00143', 'HG00144', 'HG00145', 'HG00146', 'HG00147', 'HG00148', 'HG00149',
                   'HG00150', 'HG00151', 'HG00152', 'HG00153', 'HG00154', 'HG00155', 'HG00156', 'HG00157', 'HG00158',
                   'HG00159', 'HG00160', 'HG00231', 'HG00232', 'HG00233', 'HG00234', 'HG00235', 'HG00236', 'HG00237',
                   'HG00238', 'HG00239', 'HG00240', 'HG00242', 'HG00243', 'HG00244', 'HG00245', 'HG00246', 'HG00247',
                   'HG00248', 'HG00249', 'HG00250', 'HG00251', 'HG00252', 'HG00253', 'HG00254', 'HG00255', 'HG00256',
                   'HG00257', 'HG00258', 'HG00259', 'HG00260', 'HG00261', 'HG00262', 'HG00263', 'HG00264', 'HG00265',
                   'HG01334', 'HG01789', 'HG01790', 'HG01791', 'HG02215', 'HG04301', 'HG04302', 'HG04303'],
           'khv': ['HG01595', 'HG01596', 'HG01597', 'HG01598', 'HG01599', 'HG01600', 'HG01840', 'HG01841', 'HG01842',
                   'HG01843', 'HG01844', 'HG01845', 'HG01846', 'HG01847', 'HG01848', 'HG01849', 'HG01850', 'HG01851',
                   'HG01852', 'HG01853', 'HG01855', 'HG01857', 'HG01858', 'HG01859', 'HG01860', 'HG01861', 'HG01862',
                   'HG01863', 'HG01864', 'HG01865', 'HG01866', 'HG01867', 'HG01868', 'HG01869', 'HG01870', 'HG01871',
                   'HG01872', 'HG01873', 'HG01874', 'HG01878', 'HG02015', 'HG02016', 'HG02017', 'HG02018', 'HG02019',
                   'HG02020', 'HG02021', 'HG02023', 'HG02024', 'HG02025', 'HG02026', 'HG02027', 'HG02028', 'HG02029',
                   'HG02030', 'HG02031', 'HG02032', 'HG02035', 'HG02040', 'HG02046', 'HG02047', 'HG02048', 'HG02049',
                   'HG02050', 'HG02056', 'HG02057', 'HG02058', 'HG02059', 'HG02060', 'HG02061', 'HG02064', 'HG02067',
                   'HG02068', 'HG02069', 'HG02070', 'HG02071', 'HG02072', 'HG02073', 'HG02074', 'HG02075', 'HG02076',
                   'HG02077', 'HG02078', 'HG02079', 'HG02080', 'HG02081', 'HG02082', 'HG02083', 'HG02084', 'HG02085',
                   'HG02086', 'HG02087', 'HG02088', 'HG02113', 'HG02116', 'HG02120', 'HG02121', 'HG02122', 'HG02126',
                   'HG02127', 'HG02128', 'HG02129', 'HG02130', 'HG02131', 'HG02132', 'HG02133', 'HG02134', 'HG02135',
                   'HG02136', 'HG02137', 'HG02138', 'HG02139', 'HG02140', 'HG02141', 'HG02142', 'HG02512', 'HG02513',
                   'HG02514', 'HG02521', 'HG02522', 'HG02523', 'HG02524', 'HG02525', 'HG02526'],
           'pjl': ['HG01583', 'HG01586', 'HG01589', 'HG01590', 'HG01593', 'HG01594', 'HG02490', 'HG02491', 'HG02492',
                   'HG02493', 'HG02494', 'HG02495', 'HG02597', 'HG02599', 'HG02600', 'HG02601', 'HG02602', 'HG02603',
                   'HG02604', 'HG02605', 'HG02648', 'HG02649', 'HG02650', 'HG02651', 'HG02652', 'HG02653', 'HG02654',
                   'HG02655', 'HG02656', 'HG02657', 'HG02658', 'HG02659', 'HG02660', 'HG02661', 'HG02662', 'HG02681',
                   'HG02682', 'HG02683', 'HG02684', 'HG02685', 'HG02686', 'HG02687', 'HG02688', 'HG02689', 'HG02690',
                   'HG02691', 'HG02692', 'HG02694', 'HG02696', 'HG02697', 'HG02698', 'HG02699', 'HG02700', 'HG02701',
                   'HG02724', 'HG02725', 'HG02726', 'HG02727', 'HG02728', 'HG02729', 'HG02731', 'HG02733', 'HG02734',
                   'HG02735', 'HG02736', 'HG02737', 'HG02738', 'HG02774', 'HG02775', 'HG02776', 'HG02778', 'HG02779',
                   'HG02780', 'HG02781', 'HG02783', 'HG02784', 'HG02785', 'HG02786', 'HG02787', 'HG02788', 'HG02789',
                   'HG02790', 'HG02791', 'HG02792', 'HG02793', 'HG02794', 'HG03015', 'HG03016', 'HG03017', 'HG03018',
                   'HG03019', 'HG03021', 'HG03022', 'HG03023', 'HG03228', 'HG03229', 'HG03230', 'HG03234', 'HG03235',
                   'HG03236', 'HG03237', 'HG03238', 'HG03239', 'HG03487', 'HG03488', 'HG03489', 'HG03490', 'HG03491',
                   'HG03492', 'HG03618', 'HG03619', 'HG03620', 'HG03621', 'HG03624', 'HG03625', 'HG03626', 'HG03629',
                   'HG03631', 'HG03633', 'HG03634', 'HG03635', 'HG03636', 'HG03638', 'HG03639', 'HG03640', 'HG03641',
                   'HG03649', 'HG03650', 'HG03651', 'HG03652', 'HG03653', 'HG03654', 'HG03656', 'HG03657', 'HG03660',
                   'HG03663', 'HG03667', 'HG03668', 'HG03669', 'HG03699', 'HG03700', 'HG03701', 'HG03702', 'HG03703',
                   'HG03704', 'HG03705', 'HG03706', 'HG03707', 'HG03708', 'HG03709', 'HG03710', 'HG03761', 'HG03762',
                   'HG03763', 'HG03765', 'HG03766', 'HG03767', 'HG03769'],
           'ibs': ['HG01500', 'HG01501', 'HG01502', 'HG01503', 'HG01504', 'HG01505', 'HG01506', 'HG01507', 'HG01508', 'HG01509', 'HG01510', 'HG01511', 'HG01512', 'HG01513', 'HG01514', 'HG01515', 'HG01516', 'HG01517', 'HG01518', 'HG01519', 'HG01520', 'HG01521', 'HG01522', 'HG01523', 'HG01524', 'HG01525', 'HG01526', 'HG01527', 'HG01528', 'HG01529', 'HG01530', 'HG01531', 'HG01532', 'HG01536', 'HG01537', 'HG01538', 'HG01601', 'HG01602', 'HG01603', 'HG01604', 'HG01605', 'HG01606', 'HG01607', 'HG01608', 'HG01609', 'HG01610', 'HG01611', 'HG01612', 'HG01613', 'HG01614', 'HG01615', 'HG01616', 'HG01617', 'HG01618', 'HG01619', 'HG01620', 'HG01621', 'HG01622', 'HG01623', 'HG01624', 'HG01625', 'HG01626', 'HG01627', 'HG01628', 'HG01629', 'HG01630', 'HG01631', 'HG01632', 'HG01633', 'HG01667', 'HG01668', 'HG01669', 'HG01670', 'HG01671', 'HG01672', 'HG01673', 'HG01674', 'HG01675', 'HG01676', 'HG01677', 'HG01678', 'HG01679', 'HG01680', 'HG01681', 'HG01682', 'HG01683', 'HG01684', 'HG01685', 'HG01686', 'HG01687', 'HG01694', 'HG01695', 'HG01696', 'HG01697', 'HG01698', 'HG01699', 'HG01700', 'HG01701', 'HG01702', 'HG01703', 'HG01704', 'HG01705', 'HG01706', 'HG01707', 'HG01708', 'HG01709', 'HG01710', 'HG01711', 'HG01746', 'HG01747', 'HG01748', 'HG01755', 'HG01756', 'HG01757', 'HG01761', 'HG01762', 'HG01763', 'HG01764', 'HG01765', 'HG01766', 'HG01767', 'HG01768', 'HG01769', 'HG01770', 'HG01771', 'HG01772', 'HG01773', 'HG01774', 'HG01775', 'HG01776', 'HG01777', 'HG01778', 'HG01779', 'HG01780', 'HG01781', 'HG01782', 'HG01783', 'HG01784', 'HG01785', 'HG01786', 'HG01787', 'HG02217', 'HG02218', 'HG02219', 'HG02220', 'HG02221', 'HG02222', 'HG02223', 'HG02224', 'HG02225', 'HG02229', 'HG02230', 'HG02231', 'HG02232', 'HG02233', 'HG02234', 'HG02235', 'HG02236', 'HG02237', 'HG02238', 'HG02239', 'HG02240']
           }

pops = pop_list.split(',')
final_ind_set = []

for each_pop in pops:
    if 'ALL' in pop_list:
        for l_each_pop in pop_dic.values():
            for each_ind in l_each_pop:
                final_ind_set.append(each_ind)
    else:
        if each_pop.lower() in pop_dic:
            for x_each_pop in pop_dic[each_pop.lower()]:
                final_ind_set.append(x_each_pop)


# print final_ind_set

for j in sorted(all_haplo):  # another easier way to sorted a dictionary by key, only contain key
    if j[:7] in final_ind_set:
        # print j[:7]
        output.write('>' + j + '\n')
        output.write(all_haplo[j] + '\n')

endTime = time.time()
workTime = endTime - startTime

print 'Time used: {}'.format(str(datetime.timedelta(seconds=workTime)))
print 'Erica is a genius!'
output.close()
