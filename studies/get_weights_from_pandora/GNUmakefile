
CXX=g++

CFLAGS=`root-config --cflags`
INCLUDES=`root-config --incdir`
LDLIBS=`root-config --libs`


all: inspect_weights

clean:
	rm inspect_weights.o inspect_weights

inspect_weights: inspect_weights.cxx
	$(CXX) $(CFLAGS) -c $^ -o $@.o
	$(CXX) $@.o $(LDLIBS) -o $@
