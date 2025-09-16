# Makefile for ROOT dictionary generation
CXX = g++
ROOTCFLAGS = $(shell root-config --cflags)
ROOTLIBS = $(shell root-config --libs)
ROOTGLIBS = $(shell root-config --glibs)

# Dictionary source and object files
DICT_SRC = mapDict.cxx
DICT_OBJ = mapDict.o
DICT_LIB = libMapDict.so

# Build flags
CXXFLAGS = -fPIC $(ROOTCFLAGS)
LDFLAGS = -shared $(ROOTLIBS)

# Default target
all: $(DICT_LIB)

# Generate dictionary
$(DICT_SRC): MapTypes.h LinkDef.h calcEventWeightVariations.h
	@echo "Generating dictionary..."
	rootcling -f $(DICT_SRC) -rmf libMapDict.rootmap -rml libMapDict.so MapTypes.h calcEventWeightVariations.h LinkDef.h

# Compile event weight calculator
calcEventWeightVariations.o: calcEventWeightVariations.cc calcEventWeightVariations.h
	@echo "Compile calcEventWeightVariations..."
	$(CXX) $(CXXFLAGS) -c calcEventWeightVariations.cc -o calcEventWeightVariations.o

# Compile dictionary
$(DICT_OBJ): $(DICT_SRC)
	@echo "Compiling dictionary..."
	$(CXX) $(CXXFLAGS) -c $(DICT_SRC) -o $(DICT_OBJ)

# Create shared library
$(DICT_LIB): $(DICT_OBJ) calcEventWeightVariations.o
	@echo "Creating shared library..."
	$(CXX) $(LDFLAGS) $(DICT_OBJ) calcEventWeightVariations.o -o $(DICT_LIB)

# Clean target
clean:
	rm -f $(DICT_SRC) $(DICT_OBJ) calcEventWeightVariations.o $(DICT_LIB) mapDict_rdict.pcm libMapDict.rootmap

.PHONY: all clean
