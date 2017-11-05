PROJECT(rdjpgcom C CXX)
cmake_minimum_required(VERSION 2.8)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
CONAN_BASIC_SETUP()

#find_package("LIBJPEG")
#IF (LIBJPEG_FOUND)
    ADD_EXECUTABLE(rdjpgcom rdjpgcom.c)
    include_directories(${LIBJPEG_INCLUDE_DIRS})
    TARGET_LINK_LIBRARIES(rdjpgcom ${CONAN_LIBS})
#ELSE()
#     MESSAGE(FATAL_ERROR "libjpeg not found")
#ENDIF()