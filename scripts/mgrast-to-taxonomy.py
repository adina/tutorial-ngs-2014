import sys
import os
import json
import urllib
import subprocess

def ssids_of_interest(file_in):
    l = []
    for line in file_in:
        l.append(line.rstrip().split(' ')[0])
    return l

def m5nr_to_taxid(m5nr):
    proc = subprocess.Popen(["curl", "http://api.metagenomics.anl.gov//m5nr/md5/" + m5nr + "?source=GenBank"], stdout=subprocess.PIPE)
    (out, err) = proc.communicate()
    d = json.loads(out)
    for x in d['data']:
        if x.has_key('ncbi_tax_id'):
            l = [x['md5'], x['ncbi_tax_id']]
        else:
            x['ncbi_tax_id'] = "NA"
            l = [x['md5'], x['ncbi_tax_id']]
        taxid = l[1]
        return(taxid)

def taxid_to_taxonomy(taxid):
    url = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=taxonomy&id=" + taxid + "&retmode=xml"
    proc = subprocess.Popen(["curl", url], stdout=subprocess.PIPE)
    (out, err) = proc.communicate()

    l = []
    for line in out.split('\n'):
        if line.strip().startswith("<ScientificName>"):
            dat = line.strip().split('<ScientificName>')[1].split('</ScientificName>')[0]
            l.append(dat)
    l.insert(0, taxid)
    taxonomy = ';'.join(l)
    return(taxonomy)

def parse_ssid_file(file_in, ssid_of_interest_list):
    data_l = []
    for line in file_in:
        if line.startswith('mgm'):
            dat = line.rstrip().split('\t')
            contig, m5nr, id, score, evalue, ssids = dat[0], dat[1], dat[3], dat[4], dat[-3], dat[-1]
            only_once_counter = 0
            for x in ssids.split(';'):
                if x in ssid_of_interest_list and only_once_counter == 0:
                    taxid = m5nr_to_taxid(m5nr)
                    if taxid is None:
                        taxonomy = "NA"
                    else:
                        print m5nr, taxid
                        taxonomy = taxid_to_taxonomy(str(taxid))
                        
                    only_once_counter += 1
                    l = [contig, m5nr, id, score, evalue, ssids, taxonomy]
                    data_l.append(l)
    return(data_l)
            
def get_taxa(file_in):
    d = {}
    for line in file_in:
        dat = line.rstrip().split('\t')
        m5nr, taxa = dat[0], dat[2]
        d[m5nr] = taxa
    return d


if __name__ == '__main__':
    f1 = open(sys.argv[1]) #selected ssids
    f2 = open(sys.argv[2]) #ssid mgrast file
  
    ssids_select = ssids_of_interest(f1.readlines())
    output_l = parse_ssid_file(f2.readlines(), ssids_select)
    f3 = open(sys.argv[3], 'w')
    for x in output_l:
        f3.write('%s\n' % '\t'.join(x))

