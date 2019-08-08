fnames[0]=resources/instances/2-FullIns_3.col
fnames[1]=resources/instances/3-Insertions_3.col
fnames[2]=resources/instances/david.col
fnames[3]=resources/instances/DSJC125.1.col
fnames[4]=resources/instances/games120.col
fnames[5]=resources/instances/jean.col
fnames[6]=resources/instances/miles250.col
fnames[7]=resources/instances/myciel4.col
fnames[8]=resources/instances/queen6_6.col
fnames[9]=resources/instances/r250.1.col

models=(AS ASSB PO POST)

opts=(--no-presolving)

ulimit -t 120

for fname in ${fnames[*]}
do
for model in ${models[*]}
do
for opt in ${opts[*]}
do
{ time python3 src/assignment3_run.py $model $fname $opt ; printf "\n\n" ; } &>> stuff/res2 ;
done
done
done
