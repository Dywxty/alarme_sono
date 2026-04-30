# #vem da biblioteca OpenCV - usada para a captura de video e desenho no tela
# import cv2
# #usado para cálculos matemáticos
# import numpy as np
# #threading - usado para executar funções em paralelo (simultaneamente)
# import threading
# #Usado para carregar arquivos de mídia
# import pygame
# #mediapipe - usado para detectar pontos do rosto (olhos, face, etc)
# import mediapipe as mp
# from mediapipe.tasks import python
# from mediapipe.tasks.python import vision
#
# #inicia o sistema de audio
# pygame.mixer.init()
# #carrega o som do alarme
# pygame.mixer.music.load('alarme.mp3')
#
# #variável que controla se o alarme está ativo ou não
# alarm_on = False
#
# def tocar_alarme():
#     global alarm_on
#     #executa um laço enquanto o alarme estiver ligado
#     while alarm_on:
#         #verifica se o som inda está a tocar
#         if not pygame.mixer.music.get_busy():
#             pygame.mixer.music.play()
#
# def iniciar_alarme():
#     global alarm_on
#
#     if not alarm_on:
#         alarm_on = True
#         #liga o alarme
#
#         #cria uma thread separada para tocar o som
#         threading.Thread(target=tocar_alarme, daemon=True)
#         # daemon=True faz a thread morrer quando fechar o programa
#
# def parar_alarme():
#     global alarm_on
#     alarm_on = False
#     #desliga o alarme
#
#     #para o som
#     pygame.mixer.music.stop()
#
# def calcular_ear(pontos):
#     # EAR (Eye Aspect Ratio)
#     #é uma fórmula que mede se o olho está aberto ou fechado
#     p1, p2, p3, p4, p5, p6 = pontos
#
#     #mede distancias verticais e horizontais do olho
#     #verifica se o valor for baixo ⇾ olho fehcado
#     #valor alto ⇉ olho aberto
#     distancia = (np.linalg.norm(p2 - p6) + np.linalg.norm(p3 - p5)) / (2.0 * np.linalg.norm(p1 - p4))
#     return distancia
#
# def gerar_frames():
#     # abre a ‘webcam’ (valor 0 = camera padrão)
#     cap = cv2.VideoCapture(0)
#
#     # valor limite para o olho piscar
#     EAR_LIMITE = 0.25
#
#     #tempo para considerar sono (2 segundos)
#     TEMPO_LIMITE = 2
#
#     #frame por segundo
#     FPS = 30
#
#     frames_fechados = 0
#
#     #conta quantos frames o olho ficos fechado(2s * 30 frames)
#     max_frames = TEMPO_LIMITE * FPS
#
#     #carrega o modelo de detecção facial
#     base_options = python.BaseOptions(model_asset_path='face_landmarker.task')
#
#     option = vision.FaceLandmarkerOptions(
#         base_options=base_options,
#         running_mode=vision.RunningMode.IMAGE, #roda no modo imagem
#         num_faces=1 #detecta apenas um rosto
#     )
#     #detector de rosto
#     detector = vision.FaceLandmarker.create_from_options(options=option)
#
#     #laço infinito para capturar frames da camera
#     while True:
#         # lê um frame da camera
#         sucess, frame = cap.read()
#         if not sucess:
#             break
#
#         altura, largura, _ = frame.shape # _ é uma variável ignorada, vazia
#
#         #Converte as cores. OpenCV usa BGR ⇾ MediaPipe usa RGB
#         rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#
#         #Converte imagem para formato do MediaPipe
#         mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
#
#         #Detecta os pontos do rosto
#         result = detector.detect(mp_image)
#
#         #Se encontrou o rosto, continua...
#         if result.face_landmarks:
#             face = result.face_landmarks[0]
#
#             #Pontos específicos dos olhos no rosto
#             olho_esq_ids = [33, 160, 158,133, 153, 144]
#             olho_dir_ids = [362, 385, 387, 263, 373, 380]
#
#             #Converte os pontos do MediaPipe em coordenadas reais da tela
#             def get_pontos(ids):
#                 return np.array([[face[i].x * largura, face[i].y * altura]for i in ids])
#
#             #Calcula o EAR dos dois olhos e faz a média
#             ear = (calcular_ear(get_pontos(olho_esq_ids)) + calcular_ear(get_pontos(olho_dir_ids))) / 2
#
#             #Desenhar o valor
#             cv2.putText(frame, f"EAR: {ear:.2f}", (30, 40),
#                         cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
#
#             #Se olho fechado ⇾ soma frames
#             if ear < EAR_LIMITE:
#                 frames_fechados += 1
#             else:
#                 #Se abriu o olho -> zera o contador e para o alarme
#                 frames_fechados = 0
#                 parar_alarme()
#
#             #Se atingiu o tempo com o olho fechdo ⇾ toca o alarme
#             if frames_fechados >= max_frames:
#                 iniciar_alarme()
#                 #Mostra mensagem na tela
#                 cv2.putText(frame, "ACORDAAAAAAA!!!!!!!!!!!!!!!!!!", (30, 80),
#                             cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
#
#             #Converte imagem para JPEG
#             _, buffer = cv2.imencode('.jpg', frame)
#             frame_bytes = buffer.tobytes()
#
#             #Envia o frame no formato de ‘streaming’ HTTP
#             yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n'
#

import cv2
import numpy as np
import threading
import pygame
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

pygame.mixer.init()
pygame.mixer.music.load('alarme.mp3')

alarm_on = False

def tocar_alarme():
    global alarm_on
    while alarm_on:
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play()

def iniciar_alarme():
    global alarm_on
    if not alarm_on:
        alarm_on = True
        threading.Thread(target=tocar_alarme, daemon=True).start()

def parar_alarme():
    global alarm_on
    alarm_on = False
    pygame.mixer.music.stop()

def calcular_ear(pontos):
    p1, p2, p3, p4, p5, p6 = pontos

    denom = np.linalg.norm(p1 - p4)
    if denom == 0:
        return 0

    return (np.linalg.norm(p2 - p6) + np.linalg.norm(p3 - p5)) / (2.0 * denom)

def gerar_frames():
    cap = cv2.VideoCapture(0)

    EAR_LIMITE = 0.25
    TEMPO_LIMITE = 2
    FPS = 30

    frames_fechados = 0
    max_frames = TEMPO_LIMITE * FPS

    base_options = python.BaseOptions(model_asset_path='face_landmarker.task')

    options = vision.FaceLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.VIDEO,
        num_faces=1
    )

    detector = vision.FaceLandmarker.create_from_options(options)

    timestamp = 0

    while True:
        sucess, frame = cap.read()
        if not sucess:
            break

        altura, largura, _ = frame.shape

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        result = detector.detect_for_video(mp_image, timestamp)
        timestamp += 1

        if result.face_landmarks:
            face = result.face_landmarks[0]

            # pega altura e largura da tela
            h, w, _ = frame.shape

            # transforma todos os pontos do rosto em coordenadas reais
            pontos_rosto = np.array([[p.x * w, p.y * h] for p in face])

            # encontra os limites do rosto
            x_min = int(np.min(pontos_rosto[:, 0]))
            y_min = int(np.min(pontos_rosto[:, 1]))
            x_max = int(np.max(pontos_rosto[:, 0]))
            y_max = int(np.max(pontos_rosto[:, 1]))

            # margem opcional (deixa o quadrado mais bonito)
            margem = 20
            x_min = max(0, x_min - margem)
            y_min = max(0, y_min - margem)
            x_max = min(w, x_max + margem)
            y_max = min(h, y_max + margem)

            # desenha o retângulo verde
            cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)

            olho_esq_ids = [33, 160, 158, 133, 153, 144]
            olho_dir_ids = [362, 385, 387, 263, 373, 380]

            def get_pontos(ids):
                return np.array([[face[i].x * largura, face[i].y * altura] for i in ids])

            ear = (
                calcular_ear(get_pontos(olho_esq_ids)) +
                calcular_ear(get_pontos(olho_dir_ids))
            ) / 2

            cv2.putText(frame, f"EAR: {ear:.2f}", (30, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            if ear < EAR_LIMITE:
                frames_fechados += 1
            else:
                frames_fechados = 0
                parar_alarme()

            if frames_fechados >= max_frames:
                iniciar_alarme()
                cv2.putText(frame, "ACORDA!!!", (30, 80),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)

        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


