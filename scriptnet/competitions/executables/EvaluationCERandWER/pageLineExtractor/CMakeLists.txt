cmake_minimum_required( VERSION 2.8.4 )
project( page_format_tool )
set( tool_EXE page_format_tool )
include( FindPkgConfig )
pkg_check_modules( opencv REQUIRED opencv )
pkg_check_modules( log4cxx REQUIRED liblog4cxx )
find_package( Boost COMPONENTS system filesystem thread program_options REQUIRED )

file( GLOB tool_SRC "*.cc" pugixml.cpp )
add_executable( ${tool_EXE} ${tool_SRC} )

string( REPLACE ";" " " CFLAGS_STR "${opencv_CFLAGS}" )
#string( REPLACE ";" " " CFLAGS_STR "-Wall -W ${opencv_CFLAGS}" )
set_target_properties( ${tool_EXE} PROPERTIES COMPILE_FLAGS "${CFLAGS_STR}" )

#target_link_libraries( ${tool_EXE} ${opencv_LDFLAGS} ${log4cxx_LDFLAGS} boost_system boost_program_options boost_filesystem boost_thread )
#target_link_libraries( ${tool_EXE} ${opencv_LDFLAGS} ${log4cxx_LDFLAGS} boost_system-mt boost_program_options-mt boost_filesystem-mt boost_thread-mt )
target_link_libraries( ${tool_EXE} ${opencv_LDFLAGS} ${log4cxx_LDFLAGS} ${Boost_SYSTEM_LIBRARY} ${Boost_FILESYSTEM_LIBRARY} ${Boost_THREAD_LIBRARY} ${Boost_PROGRAM_OPTIONS_LIBRARY} )

install( TARGETS ${tool_EXE} DESTINATION bin )

add_custom_target( realclean cd ${CMAKE_HOME_DIRECTORY} COMMAND rm -fr ${tool_EXE} ${tool_EXE}.exe CMakeFiles CMakeCache.txt cmake_install.cmake install_manifest.txt Makefile )
