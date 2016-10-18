TARGET = page_format_tool
SOURCE  = page_format_line_extractor.cc
AUTO_INCLUDE = `pkg-config --cflags-only-I opencv liblog4cxx eigen3`

#--------------------------------------------------------------------------------------
COMMONDIR = .
INSTALLDIR= ../BIN
AUTO_INCLUDE = `pkg-config --cflags-only-I opencv liblog4cxx eigen3`
MANUAL_INCLUDE = -I$(COMMONDIR) -I/opt/local/include/ 
INCLUDE = $(AUTO_INCLUDE) $(MANUAL_INCLUDE)
AUTO_LIBS = `pkg-config liblog4cxx opencv eigen3 --libs`
#MANUAL_LIBS = -lboost_system-mt -lboost_program_options-mt -lboost_filesystem-mt -lboost_thread-mt
MANUAL_LIBS = -lboost_system -lboost_program_options -lboost_filesystem -lboost_thread
EXTERNAL_LIBS = $(AUTO_LIBS) $(MANUAL_LIBS)

#--------------------------------------------------------------------------------------
PFT_LIBS = $(COMMONDIR)/pugixml.o $(COMMONDIR)/line_region_list.o $(COMMONDIR)/page_file.o $(COMMONDIR)/image.o $(COMMONDIR)/line_histogram.o $(COMMONDIR)/algorithm_kmeans.o $(COMMONDIR)/grey_level_histogram.o
#--------------------------------------------------------------------------------------
COPTIONS = -c -O3 -pthread -o
#COPTIONS = -c -O0 -g -o 
LOPTIONS = -O3 -o
#LOPTIONS = -O0 -g -o


.PNONY:
all: $(TARGET)

image.o: image.cc image.hpp line_histogram.hpp
	$(CXX) $(COPTIONS) $@ $< $(INCLUDE)

grey_level_histogram.o: grey_level_histogram.cc grey_level_histogram.hpp
	$(CXX) $(COPTIONS) $@ $< $(INCLUDE)

algorithm_kmeans.o: algorithm_kmeans.cc algorithm_kmeans.hpp
	$(CXX) $(COPTIONS) $@ $< $(INCLUDE) 

line_histogram.o: line_histogram.cc line_histogram.hpp algorithm_kmeans.hpp
	$(CXX) $(COPTIONS) $@ $< $(INCLUDE)

pugixml.o: pugixml.cpp pugixml.hpp pugiconfig.hpp
	$(CXX) $(COPTIONS) $@ $< $(INCLUDE)

line_region_list.o: line_region_list.cc line_region_list.hpp
	$(CXX) $(COPTIONS) $@ $< $(INCLUDE)

page_file.o: page_file.cc page_file.hpp
	$(CXX) $(COPTIONS) $@ $< $(INCLUDE)

page_format_line_extractor.o: $(SOURCE)
	$(CXX) $(COPTIONS) $@ $< $(INCLUDE)

$(TARGET): page_format_line_extractor.o $(PFT_LIBS) 
	$(CXX) $(LDFLAGS) $(LOPTIONS) $@ $^  $(INCLUDE) $(EXTERNAL_LIBS)

clean:
	rm -rf *.o
	rm -f $(TARGET)
