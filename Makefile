# Note: This is meant for Metabolite-Atlas developer use only
.PHONY: all clean test cover release gh-pages docs

export TEST_ARGS=--exe -v --with-doctest
export NAME=metatlas
export GHP_MSG="Generated gh-pages for `git log master -1 --pretty=short --abbrev-commit`"
export VERSION=`python -c "import $(NAME); print($(NAME).__version__)"`

all: clean
	python setup.py install

clean:
	rm -rf build
	rm -rf dist
	find . -name "*.pyc" -o -name "*.py,cover"| xargs rm -f

test: clean
	python setup.py build
	export PYTHONWARNINGS="all"; cd build; nosetests $(TEST_ARGS) $(NAME)
	make clean

cover: clean
	pip install nose-cov
	nosetests $(TEST_ARGS) --with-cov --cov $(NAME) $(NAME)
	coverage annotate

release: test gh-pages
	pip install wheel
	python setup.py register
	python setup.py bdist_wheel upload
	python setup.py sdist --formats=gztar,zip upload
	git tag v$(VERSION)
	git push origin --all
	git push origin --tags


deploy: gh-pages
	rsync -rv metatlas jtouma@corigrid.nersc.gov:/project/projectdirs/metatlas/anaconda/lib/python2.7/site-packages
	git push origin --all

docs: clean
	export SPHINXOPTS=-W
	pip install sphinx-bootstrap-theme numpydoc sphinx ghp-import
	make -C docs html

gh-pages:
	git checkout master
	git pull origin master
	git push origin; true
	make docs
	ghp-import -n -p -m $(GHP_MSG) docs/_build/html
