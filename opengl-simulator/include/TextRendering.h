#ifndef TEXT_RENDERING_H
#define TEXT_RENDERING_H

#include <GL/glut.h>
#include <GL/freeglut.h>

#include "CustomTypes.h"


float window_matrix[16];


void renderStringOnScreen(
    float x, float y, 
    void* font, const char* string, 
    ubyte_t r, ubyte_t g, ubyte_t b
)
{
    glPushAttrib(GL_COLOR_BUFFER_BIT);
    {
        glMatrixMode(GL_PROJECTION);
        glPushMatrix();
        {
            glLoadMatrixf(window_matrix);
            // glDisable(GL_LIGHTING);

            glColor4ub(r, g, b, 0xFF);
            glRasterPos2f(x, y);
            
            glutBitmapString(font, (const unsigned char*)string);
            //glEnable(GL_LIGHTING);
        }
        glPopMatrix();
    }
    glPopAttrib();
}

void renderStringInWorld3f(
    float x, float y, float z, 
    void* font, const char* string, 
    byte_t r, byte_t g, byte_t b
)
{
    glColor3ub(r, g, b);
    glRasterPos3f(x, y, z);
    for (int i = 0; string[i] != '\0'; ++i)
        glutBitmapCharacter(font, string[i]);
}


void renderStringInWorld3d(
    double x, double y, double z, 
    void* font, const char* string, 
    byte_t r, byte_t g, byte_t b
)
{
    glColor3ub(r, g, b);
    glRasterPos3d(x, y, z);
    for (int i = 0; string[i] != '\0'; ++i)
        glutBitmapCharacter(font, string[i]);
}


void renderStringInWorld3fv(
    vector3f pos, 
    void* font, const char* string, 
    byte_t r, byte_t g, byte_t b
)
{
    glColor3ub(r, g, b);
    glRasterPos3f(pos[0], pos[1] + 0.1f, pos[2]);
    for (int i = 0; string[i] != '\0'; ++i)
        glutBitmapCharacter(font, string[i]);
}

void renderStringInWorld3dv(
    vector3d pos, 
    void* font, const char* string, 
    byte_t r, byte_t g, byte_t b
)
{
    glColor3ub(r, g, b);
    glRasterPos3d(pos[0], pos[1] + 0.1, pos[2]);
    for (int i = 0; string[i] != '\0'; ++i)
        glutBitmapCharacter(font, string[i]);
}


#endif // TEXT_RENDERING_H