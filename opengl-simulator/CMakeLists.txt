CMAKE_MINIMUM_REQUIRED(VERSION 3.1 FATAL_ERROR)

PROJECT(solar_system LANGUAGES C)

INCLUDE_DIRECTORIES(
    "${PROJECT_SOURCE_DIR}/include"
    "${PROJECT_SOURCE_DIR}/dependencies/freeglut/include"
)

# Specify the library directories
IF (WIN32)
    IF (MSVC)
        LINK_DIRECTORIES("${PROJECT_SOURCE_DIR}/dependencies/freeglut/build/lib/Release")
    ENDIF()
ENDIF ()

IF (UNIX AND NOT APPLE)
    IF (CMAKE_C_COMPILER_ID STREQUAL "GNU")
        LINK_DIRECTORIES("${PROJECT_SOURCE_DIR}/dependencies/freeglut/build/lib")
    ENDIF()
ENDIF()

# Add source files
FILE(GLOB SOURCES "src/main.c")

# Add the executable target
ADD_EXECUTABLE(${PROJECT_NAME} ${SOURCES})

# Set C11 standard for this specific target
SET_TARGET_PROPERTIES(${PROJECT_NAME} PROPERTIES
    C_STANDARD 11
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

# Link libraries
IF (WIN32)
    IF (MSVC)
        TARGET_LINK_LIBRARIES(${PROJECT_NAME} freeglut)

        # Post-build step to copy the DLL
        ADD_CUSTOM_COMMAND(
            TARGET ${PROJECT_NAME} POST_BUILD
            COMMAND ${CMAKE_COMMAND} -E copy_if_different
            "${CMAKE_SOURCE_DIR}/dependencies/freeglut/build/bin/Release/freeglut.dll"
            $<TARGET_FILE_DIR:${PROJECT_NAME}>
        )
    ENDIF ()
ENDIF()


IF (UNIX AND NOT APPLE)
    IF (CMAKE_C_COMPILER_ID STREQUAL "GNU")
        TARGET_LINK_LIBRARIES(${PROJECT_NAME} 
            -lm
            -lGL
            -lGLU
            -lglut
        )
    ENDIF()
ENDIF()
