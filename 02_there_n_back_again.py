import time
import krpc

turn_start_altitude = 250
turn_end_altitude = 45000
target_altitude = 150000

# Configurando o servidor
conn = krpc.connect(name='HelloSpace')
vessel = conn.space_center.active_vessel

# Configurando a telemetria
ut = conn.add_stream(getattr, conn.space_center, 'ut')
altitude = conn.add_stream(getattr, vessel.flight(), 'mean_altitude')
apoapsis = conn.add_stream(getattr, vessel.orbit, 'apoapsis_altitude')

# Configuração de pré-lançamento
vessel.control.sas = False
vessel.control.rcs = False
vessel.control.throttle = 1.0

# Contação regressiva...
print('3...')
time.sleep(1)
print('2...')
time.sleep(1)
print('1...')
time.sleep(1)
print('Vai filhão!\n')

# Ativando os boosters
vessel.control.activate_next_stage()
vessel.auto_pilot.engage()
vessel.auto_pilot.target_pitch_and_heading(90, 90)
time.sleep(42)
vessel.control.activate_next_stage()

# Ativando o primeiro estágio
time.sleep(1)
vessel.control.activate_next_stage()

# Loop subida principal
turn_angle = 0
while True:

    # Curva gravitacional
    if altitude() > turn_start_altitude and altitude() < turn_end_altitude:
        frac = ((altitude() - turn_start_altitude) /
                (turn_end_altitude - turn_start_altitude))
        new_turn_angle = frac * 90
        if abs(new_turn_angle - turn_angle) > 0.5:
            turn_angle = new_turn_angle
            vessel.auto_pilot.target_pitch_and_heading(90-turn_angle, 90)
        
    # Diminua o acelerador ao se aproximar do AP
    if apoapsis() > target_altitude*0.9:
        print('Aproximando do alvo AP')
        break

# Desliga o motor quando o alvo AP for atingido
vessel.control.throttle = 0.25
while apoapsis() < target_altitude:
    print("Aguardando AP..")
    time.sleep(25)

print('AP atingido\n')
vessel.control.throttle = 0.0
time.sleep(1)

# Separação do primeiro estágio
vessel.control.activate_next_stage()
vessel.auto_pilot.disengage()

# Espere até sair da atmosfera
print('Indo para fora da atmosfera')
while altitude() < 70000:
    pass

print("Desacoplamento confirmado!")
print("Aguardando queima de circularização de órbita..")
print('Altitude agora: %.1f' % altitude())

while altitude() < 100000:
    pass

# Ativa o segundo estágio
# Queima de circularização de órbita
print('Altitude now: %.1f' % altitude())
vessel.control.throttle = 1
vessel.control.activate_next_stage()
time.sleep(8)
vessel.control.throttle = 0.0
time.sleep(2)

print("\nAguardando a altitude necessária para reentrar..")
while True:

    # Configurando retrograde e iniciando a queima de reentrada
    if altitude() < 100000:
        vessel.control.sas = True
        time.sleep(4)
        vessel.control.sas_mode = conn.space_center.SASMode.retrograde
        time.sleep(4)
        vessel.control.throttle = 1
        time.sleep(11)
        vessel.control.throttle = 0.0
        time.sleep(1)
        vessel.control.activate_next_stage()
        break
    else:
        pass

print("Esperando a altitude necessária para abrir o paraquedas..")
while True:
    # Ativando o paraquedas
    if altitude() < 4000:
        vessel.control.activate_next_stage()
        break
    else:
        pass

print("Missão Completa!")
