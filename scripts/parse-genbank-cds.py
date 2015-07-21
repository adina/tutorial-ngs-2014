import sys 
from Bio import SeqIO
from Bio.SeqRecord import SeqRecord


genome=SeqIO.read(sys.argv[1], 'genbank')

n = 0
l = []

for record in list(SeqIO.parse(sys.argv[1], 'genbank')):
    org = record.annotations["source"]
    for feat in genome.features:
        if feat.type == "CDS":
            protein_id =  feat.qualifiers['protein_id'][0]
            name = feat.qualifiers['product'][0]
            start = feat.location.start.position
            end = feat.location.end.position
            pos = [start, end]
            l.append(pos)
            print ">" + sys.argv[1].split('.')[0] + '_' + protein_id+ '\t'+ name
            print feat.extract(genome.seq)
