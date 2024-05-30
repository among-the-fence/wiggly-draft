rm -rf data
mkdir data
pushd data
git clone --depth 1 https://github.com/game-datacards/datasources.git
git clone --depth 1 https://github.com/BSData/wh40k-10e.git
pushd datasources
rm -rf .git*
popd
pushd wh40k-10e
rm -rf .git*
popd
