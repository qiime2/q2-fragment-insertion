conda: ci/recipe/meta.yaml
	# update your conda
	conda update -q -y -c defaults --override-channels conda
	conda update -q -y -c defaults --override-channels conda-build

	# build the conda package
	conda build \
		-c https://conda.anaconda.org/qiime2/label/r2017.12 \
		-c https://conda.anaconda.org/conda-forge \
		-c defaults \
		-c https://conda.anaconda.org/bioconda \
		-c https://conda.anaconda.org/biocore \
		-c https://conda.anaconda.org/sjanssen2 \
		--override-channels ci/recipe/
