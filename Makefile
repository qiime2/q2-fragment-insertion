conda: ci/recipe/meta.yaml
	conda build \
		-c https://conda.anaconda.org/qiime2/label/r2017.10 \
		-c https://conda.anaconda.org/conda-forge \
		-c defaults \
		-c https://conda.anaconda.org/bioconda \
		-c https://conda.anaconda.org/biocore \
		--override-channels ci/recipe/