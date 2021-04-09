FEED?="../feed-prpl"

all:
	if [ ! -d "./output" ]; then \
		mkdir output; \
	fi
	python3 gen_tree_dot.py $(FEED) ./output/out.dot ./output/licenses.txt
	dot -Tpng ./output/out.dot -o ./output/out.png

usage:
	echo "make FEED=[path to your feed]"

install:
	sudo apt install graphviz

clean:
	rm -rf ./output