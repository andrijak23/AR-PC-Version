import cv2
import numpy as np
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from objloader import *
from OpenGL.GL import *
from PIL import Image

cap = cv2.VideoCapture(0)
INVERSE_MATRIX = np.array([[ 1.0, 1.0, 1.0, 1.0],[-1.0,-1.0,-1.0,-1.0],[-1.0,-1.0,-1.0,-1.0],[ 1.0, 1.0, 1.0, 1.0]])

def resize(w,h):
        ratio = 1.0* w / h
        glMatrixMode(GL_PROJECTION)
        glViewport(0,0,w,h)
        gluPerspective(45, ratio, 0.1, 100.0)


def find_arucos(frame):
    marker_ids = 0
    marker_corners = []
    rejected_candidates = []

    detector_params = cv2.aruco.DetectorParameters()
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
    detector = cv2.aruco.ArucoDetector(dictionary, detector_params)

    corners, ids, _ = detector.detectMarkers(frame, marker_corners, marker_ids, rejected_candidates)
    cv2.aruco.drawDetectedMarkers(frame, corners, ids)
    cv2.imshow("frame",frame)
    return corners, ids


def draw_background(img):
    tex_back = cv2.flip(img, 0)                                                            
    tex_back = Image.fromarray(tex_back)                                                    
    ix = tex_back.size[0]                                                                   
    iy = tex_back.size[1]                                                                   
    tex_back = tex_back.tobytes("raw","BGRX", 0, -1)                                        
    global texture_background
    texture_background = glGenTextures(1)

    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, texture_background) 
    glEnable(GL_TEXTURE_2D)
    
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)                      
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    
    glTexImage2D(GL_TEXTURE_2D, 0,GL_RGBA, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, tex_back)
    
    d = 4
    glTranslatef(0.0,0.0,-19 * d)
    glBegin(GL_QUADS)
    
    glTexCoord2fv([0.0, 1.0])
    glVertex3fv([-8.0* d, -6.0* d, 0.0])
    glTexCoord2fv([1.0, 1.0])
    glVertex3fv([ 8.0* d, -6.0* d, 0.0])
    glTexCoord2fv([1.0, 0.0]); 
    glVertex3fv( [8.0* d,  6.0* d, 0.0])
    glTexCoord2fv([0.0, 0.0])
    glVertex3fv([-8.0* d,  6.0* d, 0.0])

    glEnd( )            
    glBindTexture(GL_TEXTURE_2D, 0);                                                                                                  
    return None


def render():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    ret, frame = cap.read()
    if ret == True:
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        draw_background(frame)
        
        corners,ids = find_arucos(frame)

        try:
            lengthA = len(ids)
        except:
            lengthA = 0

        for i in range(lengthA):
            if ids[i] < 5:
                rvec, tvec, _ = cv2.aruco.estimatePoseSingleMarkers(corners[i],1,camera_matrix,dist_coeffs)
                rmtx = cv2.Rodrigues(rvec)[0]
                view_matrix = np.array([[rmtx[0][0], rmtx[0][1], rmtx[0][2], tvec[0, 0, 0]],
                                        [rmtx[1][0], rmtx[1][1], rmtx[1][2], tvec[0, 0, 1]],
                                        [rmtx[2][0], rmtx[2][1], rmtx[2][2], tvec[0, 0, 2]],
                                        [0.0, 0.0, 0.0, 1.0]])
                view_matrix = view_matrix * INVERSE_MATRIX
                view_matrix = np.transpose(view_matrix)
                
                glPushMatrix()
                glLoadMatrixd(view_matrix)
                glRotatef(90,1, 0, 0) 
                glRotatef(90, 0, 1, 0) 
                
                glTranslatef(0,0.55,0)
            
                scale_factor= 1
                glScalef(scale_factor, scale_factor, scale_factor)
                if ids[i] == 1:
                    sismis.render() 
                elif ids[i] == 2:
                    sisarka.render()
                else:
                    glutSolidCube(1)
    
                glBindTexture(GL_TEXTURE_2D, 0);                         
                glPopMatrix() 
    glutSwapBuffers()


def main():
    
    global camera_matrix, dist_coeffs, markerLength,  sismis, sisarka
    camera_matrix = np.array    ([[755.79457261,   0.        , 321.27474475],
                                [  0.        , 752.62427108, 231.74744405],
                                [  0.        ,   0.        ,   1.        ]])
    dist_coeffs = np.array([ 0.19179133, -0.68386374,  0.01216799,  0.00581574,  0.00229879])
    markerLength = 0.033
    glutInit()
    
    glutInitWindowSize(640, 480)
    glutInitWindowPosition(625, 100)
    glutInitDisplayMode(GLUT_RGB | GLUT_DEPTH | GLUT_DOUBLE)
    window_id = glutCreateWindow("OpenGL")
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClearDepth(3.0)
    sismis = OBJ('sismis/untitled.obj', swapyz=False)
    sisarka = OBJ('sisarka/untitled.obj', swapyz = False)

    glDepthFunc(GL_LESS)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)   
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST)
    
    glBindTexture(GL_TEXTURE_2D, 0)
    glDisable(GL_TEXTURE_2D) 
    glutDisplayFunc(render)
    glutIdleFunc(render)
    glutReshapeFunc(resize)
    glutMainLoop()


if __name__ == "__main__":
    main()