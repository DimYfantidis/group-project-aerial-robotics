#if defined(_MSC_VER) && !defined(_CRT_SECURE_NO_WARNINGS)
#   define _CRT_SECURE_NO_WARNINGS
#endif 

#if defined(_MSC_VER) && !defined(_USE_MATH_DEFINES)
#   define _USE_MATH_DEFINES
#endif 

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <GL/glut.h>

#include "PID.h"
#include "Timer.h"
#include "KeyboardCallback.h"
#include "TextRendering.h"

#define FRAMES_PER_SEC  100.0


int window_width = 1280;
int window_height = 720;
int window_id;

PID up_pid;
PID right_pid;

double dragging_speed = 1.0;

uint64_t refresh_ts;


void display(void)
{
    if (keystrokes[27]) 
    {
        glutDestroyWindow(window_id);
        glutLeaveMainLoop();
        return;
    }

    uint64_t current_ts = getAbsoluteTimeMillis();
    
    double dt_sec = (current_ts - refresh_ts) / 1000.0;

    if (dt_sec < 1.0 / FRAMES_PER_SEC)
    {
        glutPostRedisplay();
        return;
    }
    refresh_ts = current_ts;

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    gluPerspective(60.0, 16.0 / 9.0, 0.01, 400.0);


    gluLookAt(
        -80, 120, -80,
        8.110778, 0.000000, -39.169060,
        .0, 1.0, .0
    );

    glMatrixMode(GL_MODELVIEW);
    glLoadIdentity();

    static double u = 30.0;
    static double d = -30.0;
    static double l = -30.0;
    static double r = 30.0;

    vector3d p1 = {u, 0, l};
    vector3d p2 = {u, 0, r};
    vector3d p3 = {d, 0, r};
    vector3d p4 = {d, 0, l};
    
    glColor3ub(17, 124, 19);
    glBegin(GL_QUADS);
    {
        glVertex3dv(p1);
        glVertex3dv(p2);
        glVertex3dv(p3);
        glVertex3dv(p4);
    }
    glEnd();

    static double height = 50.0;

    static bool height_selected = false;

    keyToggle('H', &height_selected, 200);

    if (height_selected)
    {
        if (arrow_up_loaded) 
        {
            height += 1.0 * dragging_speed * dt_sec;
            if (height > 120.0)
                height = 120.0;
        }
        if (arrow_down_loaded) 
        {
            height -= 1.0 * dragging_speed * dt_sec;
            if (height < 5.0)
                height = 5.0;
        }
    }

    // static double h_param = -M_PI;

    // if (h_param > M_PI) {
    //     h_param -= 2.0 * M_PI;
    // }

    // h_param += 0.001;

    vector3d camera_pos = {
        (p1[0] + p2[0] + p3[0] + p4[0]) / 4.0, 
        height, 
        (p1[2] + p2[2] + p3[2] + p4[2]) / 4.0
    };
    vector3d camera_geo_coords;

#define START_LAT 51.423867
#define START_LON -2.671733

    // Longitude
    camera_geo_coords[0] = START_LAT + (camera_pos[0] / 111194.4444);
    // Could be height but I will not use it anyway so who cares
    camera_geo_coords[1] = NAN;
    // Latitude
    camera_geo_coords[2] = START_LON + (camera_pos[2] / 111194.4444 * cos(DEG_TO_RAD(START_LAT)));

    vector3d v1 = { 
        p1[0] - camera_pos[0], p1[1] - camera_pos[1], p1[2] - camera_pos[2],
    };
    vector3d v2 = { 
        p2[0] - camera_pos[0], p2[1] - camera_pos[1], p2[2] - camera_pos[2],
    };
    vector3d v3 = { 
        p3[0] - camera_pos[0], p3[1] - camera_pos[1], p3[2] - camera_pos[2],
    };
    vector3d v4 = { 
        p4[0] - camera_pos[0], p4[1] - camera_pos[1], p4[2] - camera_pos[2],
    };

    vector3d gmp = {
        (p1[0] + p2[0] + p3[0] + p4[0]) / 4.0, 
        .5,
        (p1[2] + p2[2] + p3[2] + p4[2]) / 4.0
    };

    glColor3ub(0xFF, 0xFF, 0xFF);
    glBegin(GL_POINTS);
    {
        // Ground corners
        glVertex3dv(p1);
        glVertex3dv(p2);
        glVertex3dv(p3);
        glVertex3dv(p4);

        // Ground middle point (GMP)
        glVertex3dv(gmp);

        // Moving point (MP)
        glColor3ub(0xA0, 0xA0, 0xFF);
        glVertex3dv(camera_pos);
    }
    glEnd();

    renderStringInWorld3dv(p1, GLUT_BITMAP_9_BY_15, "p1", 0xFF, 0xFF, 0xFF);
    renderStringInWorld3dv(p2, GLUT_BITMAP_9_BY_15, "p2", 0xFF, 0xFF, 0xFF);
    renderStringInWorld3dv(p3, GLUT_BITMAP_9_BY_15, "p3", 0xFF, 0xFF, 0xFF);
    renderStringInWorld3dv(p4, GLUT_BITMAP_9_BY_15, "p4", 0xFF, 0xFF, 0xFF);

    glBegin(GL_LINES);
    {
        // GMP-to-MP
        glColor4f(1.0f, 1.0f, 1.0f, 0.3f);
        glVertex3dv(gmp);
        glVertex3dv(camera_pos);

        // MP-to-p1
        glVertex3dv(camera_pos);
        glVertex3dv(p1);

        // MP-to-p2
        glVertex3dv(camera_pos);
        glVertex3dv(p2);
        
        // MP-to-p3
        glVertex3dv(camera_pos);
        glVertex3dv(p3);
        
        // MP-to-p4
        glVertex3dv(camera_pos);
        glVertex3dv(p4);
    }
    glEnd();


#define HORIZON_END 70.0

    // Generate Cardinal Directions
    glBegin(GL_POINTS);
    {
        // Ground corners
        glVertex3d(HORIZON_END, .0, .0);
        glVertex3d(.0, .0, HORIZON_END);
        glVertex3d(-HORIZON_END, .0, .0);
        glVertex3d(.0, .0, -HORIZON_END);
    }
    glEnd();

    renderStringInWorld3d(HORIZON_END, 1.0, .0, GLUT_BITMAP_9_BY_15, "N", 0x00, 153, 0x00);
    renderStringInWorld3d(.0, 1.0, HORIZON_END, GLUT_BITMAP_9_BY_15, "E", 0x00, 153, 0x00);
    renderStringInWorld3d(-HORIZON_END, 1.0, .0, GLUT_BITMAP_9_BY_15, "S", 200, 0x00, 0x00);
    renderStringInWorld3d(.0, 1.0, -HORIZON_END, GLUT_BITMAP_9_BY_15, "W", 200, 0x00, 0x00);


    static bool auto_mode = false;

    keyToggle('A', &auto_mode, 200);

    static bool up_selected = false;
    static bool down_selected = false; 
    static bool right_selected = false;
    static bool left_selected = false;

    if (!auto_mode)
    {
        keyToggle('U', &up_selected, 200);
        keyToggle('D', &down_selected, 200);
        keyToggle('L', &left_selected, 200);
        keyToggle('R', &right_selected, 200);
    }
    else
    {    
        up_selected = false;
        down_selected = false; 
        right_selected = false;
        left_selected = false;
    }

#define EDGE_STEP_FACTOR 0.2

    if (!up_selected && !down_selected && !left_selected && !right_selected)
    {
        if (!auto_mode)
            renderStringOnScreen(10.0f, window_height - 16.0f, GLUT_BITMAP_9_BY_15, "No direction", 0x00, 127, 0x00);
        else
            renderStringOnScreen(10.0f, window_height - 16.0f, GLUT_BITMAP_9_BY_15, "AUTO Mode", 0x00, 0xFF, 0x00);
    }
    if (up_selected) 
    {
        u += (arrow_up_loaded ? EDGE_STEP_FACTOR : (arrow_down_loaded ? -EDGE_STEP_FACTOR : .0f)) * dragging_speed * dt_sec;
        renderStringOnScreen(10.0f, window_height - 16.0f, GLUT_BITMAP_9_BY_15, "UP selected", 0x00, 0xFF, 0x00);
    }
    if (down_selected) 
    {
        d += (arrow_up_loaded ? EDGE_STEP_FACTOR : (arrow_down_loaded ? -EDGE_STEP_FACTOR : .0f)) * dragging_speed * dt_sec;
        renderStringOnScreen(10.0f, window_height - 16.0f, GLUT_BITMAP_9_BY_15, "DOWN selected", 0x00, 0xFF, 0x00);
    }
    if (right_selected) 
    {
        r += (arrow_up_loaded ? EDGE_STEP_FACTOR : (arrow_down_loaded ? -EDGE_STEP_FACTOR : .0f)) * dragging_speed * dt_sec;
        renderStringOnScreen(10.0f, window_height - 16.0f, GLUT_BITMAP_9_BY_15, "RIGHT selected", 0x00, 0xFF, 0x00);
    }
    if (left_selected)
    {
        l += (arrow_up_loaded ? EDGE_STEP_FACTOR : (arrow_down_loaded ? -EDGE_STEP_FACTOR : .0f)) * dragging_speed * dt_sec;
        renderStringOnScreen(10.0f, window_height - 16.0f, GLUT_BITMAP_9_BY_15, "LEFT selected", 0x00, 0xFF, 0x00);
    }

    double HFOV = RAD_TO_DEG(
        acos(innerProduct3dv(v1, v2) / (vectorLength3dv(v1) * vectorLength3dv(v2)))
    );
    double VFOV = RAD_TO_DEG(
        acos(innerProduct3dv(v2, v3) / (vectorLength3dv(v2) * vectorLength3dv(v3)))
    );


    static char buffer[1024];

    snprintf(buffer, sizeof(buffer), "HFOV approx.: %7.3lf\u00B0 - Expected: 45\u00B0", HFOV);
    renderStringOnScreen(160.0f, window_height - 16.0f, GLUT_BITMAP_9_BY_15, buffer, 0xFF, 0xA5, 0x00);
    snprintf(buffer, sizeof(buffer), "VFOV approx.: %7.3lf\u00B0 - Expected: 34\u00B0", VFOV);
    renderStringOnScreen(160.0f, window_height - 32.0f, GLUT_BITMAP_9_BY_15, buffer, 0xFF, 0xA5, 0x00);
    snprintf(buffer, sizeof(buffer), "Param. speed: x%7.5lf", dragging_speed);
    renderStringOnScreen(160.0f, window_height - 48.0f, GLUT_BITMAP_9_BY_15, buffer, 0xFF, 0xA5, 0x00);

    float cUIoff = 20.0f; 

    snprintf(buffer, sizeof(buffer), "Camera pos.: (%8.3lf, %8.3lf, %8.3lf)", camera_pos[0], camera_pos[1], camera_pos[2]);
    renderStringOnScreen(10.0f, window_height - 50.0f - cUIoff, GLUT_BITMAP_9_BY_15, buffer, 0xA0, 0xA0, 0xFF);
    snprintf(buffer, sizeof(buffer), "Camera geog. coords.: (%.8lf, %.8lf)", camera_geo_coords[0], camera_geo_coords[2]);
    renderStringOnScreen(10.0f, window_height - 70.0f - cUIoff, GLUT_BITMAP_9_BY_15, buffer, 0xA0, 0xA0, 0xFF);

    if (auto_mode)
    {
        u += updatePID(&up_pid, 34.0, VFOV);
        r += updatePID(&right_pid, 45.0, HFOV);
    }
    else
    {
        resetPID(&up_pid);
        resetPID(&right_pid);
    }

    snprintf(buffer, sizeof(buffer), "Perspective Corner Points w.r.t Camera:");
    renderStringOnScreen(10.0f, window_height - 90.0f - cUIoff, GLUT_BITMAP_9_BY_15, buffer, 0xA0, 0xA0, 0xFF);
    snprintf(buffer, sizeof(buffer), "> p1 = (%8.3f, %8.3f, %8.3f)", v1[0], v1[1], v1[2]);
    renderStringOnScreen(10.0f, window_height - 110.0f - cUIoff, GLUT_BITMAP_9_BY_15, buffer, 0xA0, 0xA0, 0xFF);
    snprintf(buffer, sizeof(buffer), "> p2 = (%8.3f, %8.3f, %8.3f)", v2[0], v2[1], v2[2]);
    renderStringOnScreen(10.0f, window_height - 130.0f - cUIoff, GLUT_BITMAP_9_BY_15, buffer, 0xA0, 0xA0, 0xFF);
    snprintf(buffer, sizeof(buffer), "> p3 = (%8.3f, %8.3f, %8.3f)", v3[0], v3[1], v3[2]);
    renderStringOnScreen(10.0f, window_height - 150.0f - cUIoff, GLUT_BITMAP_9_BY_15, buffer, 0xA0, 0xA0, 0xFF);
    snprintf(buffer, sizeof(buffer), "> p4 = (%8.3f, %8.3f, %8.3f)", v4[0], v4[1], v4[2]);
    renderStringOnScreen(10.0f, window_height - 170.0f - cUIoff, GLUT_BITMAP_9_BY_15, buffer, 0xA0, 0xA0, 0xFF);

    float hUIoff = 20.0f;
    
    renderStringOnScreen(10.0f, 145.0f + hUIoff, GLUT_BITMAP_9_BY_15, "HELP:", 0xFF, 0xFF, 0xFF);
    snprintf(buffer, sizeof(buffer), "> 'A': Auto Mode (%s)", (auto_mode ? "Enabled" : "Disabled"));
    renderStringOnScreen(10.0f, 120.0f + hUIoff, GLUT_BITMAP_9_BY_15, buffer, 0xFF, 0xFF, 0xFF);
    snprintf(buffer, sizeof(buffer), "> 'U': Select \"Up\" Parameter");
    renderStringOnScreen(10.0f, 105.0f + hUIoff, GLUT_BITMAP_9_BY_15, buffer, 0xFF, 0xFF, 0xFF);
    snprintf(buffer, sizeof(buffer), "> 'D': Select \"Down\" Parameter");
    renderStringOnScreen(10.0f, 90.0f + hUIoff, GLUT_BITMAP_9_BY_15, buffer, 0xFF, 0xFF, 0xFF);
    snprintf(buffer, sizeof(buffer), "> 'R': Select \"Right\" Parameter");
    renderStringOnScreen(10.0f, 75.0f + hUIoff, GLUT_BITMAP_9_BY_15, buffer, 0xFF, 0xFF, 0xFF);
    snprintf(buffer, sizeof(buffer), "> 'L': Select \"Left\" Parameter");
    renderStringOnScreen(10.0f, 60.0f + hUIoff, GLUT_BITMAP_9_BY_15, buffer, 0xFF, 0xFF, 0xFF);
    snprintf(buffer, sizeof(buffer), "> 'H': Select camera height Parameter");
    renderStringOnScreen(10.0f, 45.0f + hUIoff, GLUT_BITMAP_9_BY_15, buffer, 0xFF, 0xFF, 0xFF);
    snprintf(buffer, sizeof(buffer), "> ARROW_UP: Increase selected parameter");
    renderStringOnScreen(10.0f, 30.0f + hUIoff, GLUT_BITMAP_9_BY_15, buffer, 0xFF, 0xFF, 0xFF);
    snprintf(buffer, sizeof(buffer), "> ARROW_DOWN: Decrease selected parameter");
    renderStringOnScreen(10.0f, 15.0f + hUIoff, GLUT_BITMAP_9_BY_15, buffer, 0xFF, 0xFF, 0xFF);
    snprintf(buffer, sizeof(buffer), "> 'P': Select dummy camera object (Move within image using arrow keys)");
    renderStringOnScreen(10.0f, 0.0f + hUIoff, GLUT_BITMAP_9_BY_15, buffer, 0xFF, 0xFF, 0xFF);


    if (height_selected)
        renderStringOnScreen(10.0f, window_height - 32.0f, GLUT_BITMAP_9_BY_15, "Height Selected", 0x00, 0xFF, 0x00);
    else
        renderStringOnScreen(10.0f, window_height - 32.0f, GLUT_BITMAP_9_BY_15, "Height Locked", 0x00, 127, 0x00);       


    if (keystrokes['+']) 
    {
        dragging_speed *= 1.01;

        if (dragging_speed > 20.0)
            dragging_speed = 20.0;
    }
    if (keystrokes['-']) 
    {
        dragging_speed /= 1.01;
        
        if (dragging_speed < 1.0)
            dragging_speed = 1.0;
    }

    
    // Time to draw the image surface
    vector3d diff_horz = {
        p1[0] - p2[0],
        p1[1] - p2[1],
        p1[2] - p2[2],
    };
    vector3d diff_vert = {
        p3[0] - p2[0],
        p3[1] - p2[1],
        p3[2] - p2[2],
    };
    double diff_horz_len = vectorLength3dv(diff_horz);
    double diff_vert_len = vectorLength3dv(diff_vert);

    glColor4f(0.5, 0.5, 0.5, 0.5);
    
    glBegin(GL_QUADS);
    {
        glVertex3d(
            camera_pos[0] - 0.05 * diff_vert_len,
            camera_pos[1] - 0.1 * height,
            camera_pos[2] - 0.05 * diff_horz_len
        );
        glVertex3d(
            camera_pos[0] + 0.05 * diff_vert_len,
            camera_pos[1] - 0.1 * height,
            camera_pos[2] - 0.05 * diff_horz_len
        );
        glVertex3d(
            camera_pos[0] + 0.05 * diff_vert_len,
            camera_pos[1] - 0.1 * height,
            camera_pos[2] + 0.05 * diff_horz_len
        );
        glVertex3d(
            camera_pos[0] - 0.05 * diff_vert_len,
            camera_pos[1] - 0.1 * height,
            camera_pos[2] + 0.05 * diff_horz_len
        );
    }
    glEnd();

    // Let's try to put a sample object within the frame.
    static double dummy_obj_horz_percentage = -0.3;
    static double dummy_obj_vert_percentage = 0.2;


    glColor4ub(0x00, 0x00, 0x00, 0xFF);
    glBegin(GL_POINTS);
    {
        glVertex3d(
            camera_pos[0] + dummy_obj_vert_percentage * (0.05 * diff_vert_len), 
            camera_pos[1] - 0.095 * height, 
            camera_pos[2] + dummy_obj_horz_percentage * (0.05 * diff_horz_len)
        );
    }
    glEnd();

    vector3d model_estimation = {.0, .0, .0};
    
    model_estimation[0] = (diff_vert_len / 2) * dummy_obj_vert_percentage + camera_pos[0];
    model_estimation[2] = (diff_horz_len / 2) * dummy_obj_horz_percentage + camera_pos[2];

    vector3d model_geo_coords = {
        camera_geo_coords[0] + model_estimation[0] / 111194.44,
        NAN,
        camera_geo_coords[2] + model_estimation[2] / (111194.44 * cos(DEG_TO_RAD(camera_geo_coords[0])))
    };

    glColor4ub(0x00, 0x00, 0xFF, 0xFF);
    glBegin(GL_POINTS);
    {
        glVertex3d(
            model_estimation[0], 
            .5, 
            model_estimation[2]
        );
    }
    glEnd();

    static bool modify_point = false;

#define MODIFY_POINT_STEP 0.1

    keyToggle('P', &modify_point, 200);

    if (modify_point)
    {
        if (arrow_down_loaded)
        {
            dummy_obj_vert_percentage -= MODIFY_POINT_STEP * dragging_speed * dt_sec;
            if (dummy_obj_vert_percentage < -1.0)
                dummy_obj_vert_percentage = -1.0;
        }
        if (arrow_up_loaded)
        {
            dummy_obj_vert_percentage += MODIFY_POINT_STEP * dragging_speed * dt_sec;
            if (dummy_obj_vert_percentage > 1.0)
                dummy_obj_vert_percentage = 1.0;
        }
        if (arrow_right_loaded)
        {
            dummy_obj_horz_percentage += MODIFY_POINT_STEP * dragging_speed * dt_sec;
            if (dummy_obj_horz_percentage > 1.0)
            dummy_obj_horz_percentage = 1.0;
        }
        if (arrow_left_loaded)
        {
            dummy_obj_horz_percentage -= MODIFY_POINT_STEP * dragging_speed * dt_sec;
            if (dummy_obj_horz_percentage < -1.0)
                dummy_obj_horz_percentage = -1.0;
        }
    }

    if (modify_point)
        renderStringOnScreen(10.0f, window_height - 48.0f, GLUT_BITMAP_9_BY_15, "Sample Selected", 0x00, 0xFF, 0x00);
    else
        renderStringOnScreen(10.0f, window_height - 48.0f, GLUT_BITMAP_9_BY_15, "Sample Locked", 0x00, 127, 0x00);       


    float sobjUIoff = cUIoff + 220.0f;

    renderStringOnScreen(10.0f, window_height - sobjUIoff, GLUT_BITMAP_9_BY_15, "Sample Object: ", 0xC2, 0x66, 0xA7);
    snprintf(
        buffer, sizeof(buffer), "> Image Percentages (UP, RIGHT): (%7.2lf%%, %7.2lf%%)", 
        100 * dummy_obj_vert_percentage, 100 * dummy_obj_horz_percentage
    );
    renderStringOnScreen(10.0f, window_height - sobjUIoff - 20.0f, GLUT_BITMAP_9_BY_15, buffer, 0xC2, 0x66, 0xA7);
    snprintf(
        buffer, sizeof(buffer), "> Est. Cartesian Coordinates w.r.t GMP: (%7.3lf, %7.3lf, %7.3lf)", 
        model_estimation[0] - gmp[0], (double)0, model_estimation[2] - gmp[2]
    );
    renderStringOnScreen(10.0f, window_height - sobjUIoff - 40.0f, GLUT_BITMAP_9_BY_15, buffer, 0xC2, 0x66, 0xA7);
    snprintf(
        buffer, sizeof(buffer), "> Est. Geographical Coordinates: (%.8lf, %.8lf)", 
        model_geo_coords[0], model_geo_coords[2]
    );
    renderStringOnScreen(10.0f, window_height - sobjUIoff - 60.0f, GLUT_BITMAP_9_BY_15, buffer, 0xC2, 0x66, 0xA7);

    snprintf(buffer, sizeof(buffer), "FPS: %6.2lf", (1.0 / dt_sec));
    renderStringOnScreen(window_width - 110.0f, window_height - 16.0f, GLUT_BITMAP_9_BY_15, buffer, 0xF0, 0xF0, 0xF0);

    snprintf(buffer, sizeof(buffer), "Camera img. aspect ratio: %lf", diff_horz_len / diff_vert_len);
    renderStringOnScreen(10.0f, window_height - 190.0f - cUIoff, GLUT_BITMAP_9_BY_15, buffer, 0xA0, 0xA0, 0xFF);


    glutSwapBuffers();
    glutPostRedisplay();
}


int main(int argc, char* argv[])
{
	glutInit(&argc, argv);
	glutInitDisplayMode(GLUT_DOUBLE | GLUT_DEPTH | GLUT_RGB);
	glutInitWindowSize(window_width, window_height);
    glutInitWindowPosition(0, 0);
	window_id = glutCreateWindow("Pixel-Coordinate Mapping for UAV");
    

    // ----------- Window Matrix (BEGIN) ----------- //
	glMatrixMode(GL_PROJECTION);
	glLoadIdentity();

	// Initialization of Window Matrix for on-screen string rendering.
	glPushMatrix();
	{
		gluOrtho2D(0.0, (double)window_width, 0.0, (double)window_height);
		glGetFloatv(GL_PROJECTION_MATRIX, window_matrix);
	}
	glPopMatrix();
	// ----------- Window Matrix (END) ----------- //

    
	glClearColor(0.3f, 0.3f, 0.3f, 1.0f);
    

	glEnable(GL_DEPTH_TEST);

    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    glEnable(GL_BLEND);

    glEnable(GL_POINT_SMOOTH);
    glPointSize(6.0f);
    
    glutSetOption(GLUT_ACTION_ON_WINDOW_CLOSE, GLUT_ACTION_GLUTMAINLOOP_RETURNS);

    printf("[1] >>> Hello, Universe!\n");

    initModuleKeyboardCallback();

    glutDisplayFunc(display);
    glutKeyboardFunc(callbackKeyboardDown);
    glutKeyboardUpFunc(callbackKeyboardUp);
    glutSpecialFunc(callbackSpecialKeyboard);
    glutSpecialUpFunc(callbackSpecialUpKeyboard);


    {
        Timer* programTimer = initTimer("glutMainLoop");

        refresh_ts = getAbsoluteTimeMillis();
        
        initialisePID(&up_pid, .01, .0, .0);
        initialisePID(&right_pid, .01, .0, .0);

        glutMainLoop();
        endTimer(programTimer);
    }



    printf("[2] >>> Exited Main Loop.\n");

    
    glutExit();

    printf("[3] >>> Deallocated All Resources.\n");


    return EXIT_SUCCESS;
}
