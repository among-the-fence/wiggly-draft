rm -rf data
mkdir data
pushd data
git clone --depth 1 https://github.com/game-datacards/datasources.git
git clone --depth 1 https://github.com/BSData/wh40k-10e.git

for d in */ ; do
  echo $d.git*
  rm -rf $d.git*
done

pushd datasources
rm -rf 40k
pushd 10th
rm -rf conversion