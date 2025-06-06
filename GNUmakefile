
CXX=g++

lantern_ana/helpers/wirecell_fiducial_volume.o: lantern_ana/helpers/wirecell_fiducial_volume.cxx
	@echo "<< compile wirecell fiducial volume function >>"
	$(CXX) -c -fPIC $^ -o $@

lantern_ana/helpers/lib_wirecell_fiducial_volume.so: lantern_ana/helpers/wirecell_fiducial_volume.o
	@echo "<< linking >>"
	$(CXX) -shared -Wl,-soname,lib_wirecell_fiducial_volume.so -o $@  $^

clean:
	@rm -f lantern_ana/helpers/lib_wirecell_fiducial_volume.so lantern_ana/helpers/wirecell_fiducial_volume.o

all: lantern_ana/helpers/lib_wirecell_fiducial_volume.so 

.PHONY: all clean



