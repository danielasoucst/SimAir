# coding: utf-8
import simpy
import random

#Variavéis da Simulação
RANDOM_SEED = 42

''' Com carga leve'''
# TEMPO_POUSO = 1 #EM MINUTOS
# TEMPO_DECOLAGEM = 2
# TEMPO_ABASTECIMENTO = 2
# TEMPO_DESEMBARQUE = 1
#
# A_INTER = 7 #Create a airplane every a_inter minutes
# TEMPO_SIMULACAO = 120 #imulation time in minutes
#
# QTDE_PISTAS = 1
# QTDE_PONTES = 2
# QTDE_TANQUES = 1
#
# PROB_ABASTECIMENTO = 0.5

'''Com carga pesada de trabalho'''
TEMPO_POUSO = 1.5  #EM MINUTOS
TEMPO_DECOLAGEM = 3
TEMPO_ABASTECIMENTO = 3
TEMPO_DESEMBARQUE = 1.5

A_INTER = 4 #Create a airplane every a_inter minutes
TEMPO_SIMULACAO = 120 #imulation time in minutes

QTDE_PISTAS = 2
QTDE_PONTES = 2
QTDE_TANQUES = 3

PROB_ABASTECIMENTO = 0.5

class Simulacao:
    # Métricas de desempenho analisadas:
    # número de aviões atendidos / hora;
    # tempo médio por avião no solo
    # utilização dos fingers e das pistas.

    def __init__(self):
        self.num_chegadas = 0  # self.num_arrivals = 0
        self.num_pousos = 0 # self.num_complet = 0
        self.num_abastecimentos = 0 # self.num_refuel = 0
        self.num_desembarques = 0
        self.tempo_total_abastecimento = 0# self.num_refuel_time = 0
        self.num_decolagens = 0# self.num_departures = 0
        self.tempo_total_solo = 0

    def new_chegada(self):
        self.num_chegadas += 1

    def new_abastecimento(self, time):
        self.num_abastecimentos += 1
        self.tempo_total_abastecimento += time

    def new_decolagem(self,tempoEmSolo):
        self.num_decolagens += 1
        self.tempo_total_solo += tempoEmSolo


    def new_pouso(self):
        self.num_pousos += 1

    def new_desembarque(self):
        self.num_desembarques += 1

    def report(self):

        media_chegadas = float(self.num_chegadas) / (TEMPO_SIMULACAO)
        media_atendimento = float(self.num_decolagens) / (TEMPO_SIMULACAO)

        # PONTES
        x_pontes = float(self.num_desembarques)/float(TEMPO_SIMULACAO)
        u_pontes = float(x_pontes)*float(TEMPO_DESEMBARQUE) # Ui = Xi*Si
        u_pontes /= float(QTDE_PONTES) # utilização média para pontes

        #PISTAS
        x_pistas = float(self.num_pousos+self.num_decolagens)/float(TEMPO_SIMULACAO)
        u_pista = (float(self.num_pousos*TEMPO_POUSO)+float(self.num_decolagens*TEMPO_DECOLAGEM))/float(TEMPO_SIMULACAO) # Bi/T
        u_pista /= float(QTDE_PISTAS)

        #tanques
        x_tanque = float(self.num_abastecimentos)/float(TEMPO_SIMULACAO)
        u_tanques = float(x_tanque)*float(TEMPO_ABASTECIMENTO)
        u_tanques /= float(QTDE_TANQUES)


        print("<<<<<Métricas>>>>>>")
        print ('\n*** SimPy Simulation Report ***\n')
        print ('Total Simulation Time: %.2f (minutes)' % TEMPO_SIMULACAO)
        print ('Total Arrivals: %d (airplanes)' % self.num_chegadas)
        print ('Total Pouso: %d' % self.num_pousos)
        print ('Total Departures: %d' % self.num_decolagens)
        print ('Total Refuels: %d' % self.num_abastecimentos)
        print ('Media de chegadas: %f/min' % media_chegadas)
        print ('Num. médio de aviões atendidos: %f/min' % media_atendimento)
        print ('Tempo médio por avião no solo: %f min por aviao' % (self.tempo_total_solo/self.num_decolagens))
        print('Throughput, utilização das pontes de desemb.: %.2f/min,%.2f %%'%(x_pontes,u_pontes*100))
        print('Throughput, utilização das pistas.: %.2f,%.2f%% ' % (x_pistas, u_pista*100))
        print('Throughput, utilização dos tanques de abastecimento: %2f,%.2f %%' % (x_tanque, u_tanques*100))

class Aeroporto(object):
    def __init__(self, env,qtde_pistas,qtde_pontes,qtde_tanques,tempo_abastecimento,tempo_pouso,tempo_decolagem,tempo_desembarque):
        self.env = env
        self.pistas = simpy.Resource(env, qtde_pistas)
        self.pontes_desembarque = simpy.Resource(env,qtde_pontes)
        self.tanques = simpy.Resource(env,qtde_tanques)
        self.tempo_abastecimento = tempo_abastecimento
        self.tempo_pouso = tempo_pouso
        self.tempo_desembarque = tempo_desembarque
        self.tempo_decolagem = tempo_decolagem


    ''' Serviços oferecidos pelo aeroporto'''

    def liberar_pouso(self,aviao):
        print ('LAND - %s begins at the airport at %.2f.' % (aviao, env.now))
        yield self.env.timeout(self.tempo_pouso)
        print ('LAND - %s finishs at the airport at %.2f.' % (aviao, env.now))

    def liberar_ponte(self, aviao):
        yield self.env.timeout(self.tempo_desembarque)
        print ('FINGER - %s finishs at the airport at %.2f.' % (aviao, env.now))

    def liberar_abastecimento(self,aviao):
        yield self.env.timeout(self.tempo_abastecimento)
        print("abastecimento -  %s at %.2f ." % (aviao, env.now))

    def liberar_decolagem(self,aviao):
        yield self.env.timeout(self.tempo_decolagem)
        print("DEPARTUTE -  %s at %.2f ." % (aviao, env.now))

def aviao(env, nome, aeroporto): #o aviao é um processo

    print('%s arrives at the airport at %.2f.' % (nome, env.now))
    simulacao.new_chegada()
    tempo_chegada = env.now
    horario_pouso = 0

    '''Simulando pedido de pouso'''
    # o with libera automaticamente o recurso depois q o processo termina seu uso, passando
    # o uso assim para o proximo processo que está na fila
    with aeroporto.pistas.request() as request:
        yield request
        print('%s enters the airport at %.2f. Wait: %.2f' % (nome, env.now, env.now - tempo_chegada))
        horario_pouso = env.now
        yield env.process(aeroporto.liberar_pouso(nome))
        simulacao.new_pouso()

    with aeroporto.pontes_desembarque.request() as request:
        yield request
        print('%s requisita finger at %.2f. Wait: %.2f' % (nome, env.now, env.now - tempo_chegada))
        yield env.process(aeroporto.liberar_ponte(nome))
        simulacao.new_desembarque()

    '''Simulando pedido de abastecimento'''
    sorte = random.randint(0, 100)
    if(sorte<PROB_ABASTECIMENTO*100): #50% de chance
        with aeroporto.tanques.request() as request:
            yield request
            start = env.now
            print('%s abastece no airport at %.2f. Wait: %.2f' % (nome, env.now, env.now - tempo_chegada))
            yield env.process(aeroporto.liberar_abastecimento(nome))
            simulacao.new_abastecimento(env.now - start)


    with aeroporto.pistas.request() as request: #no caso, so temos uma pista
        yield request
        start = env.now
        estadia = env.now - horario_pouso
        print('%s sai do airport at %.2f. Wait: %.2f tempo em solo:%.2f ' % (nome, env.now, env.now - tempo_chegada,estadia))
        yield env.process(aeroporto.liberar_decolagem(nome))
        simulacao.new_decolagem(estadia)

    print('%s leaves the airport at %.2f. Service time: %.2f' % (nome, env.now, env.now - start))

def setup(env, qtde_pistas,qtde_pontes,qtde_tanques,tempo_abastecimento,tempo_pouso,tempo_decolagem,tempo_desembarque, a_inter):

    aeroporto = Aeroporto(env, qtde_pistas,qtde_pontes,qtde_tanques, tempo_abastecimento, tempo_pouso, tempo_decolagem,tempo_desembarque)

    #Cria, incialmente, 4 aviões
    for i in range(4):
        env.process(aviao(env, 'Aviao %d' % i, aeroporto))

    #Vamo botar mais avioes enquanto esta simulacao ocorre Create more cars while the simulation is running
    while True:
        yield env.timeout(random.randint(a_inter-2, a_inter+2))
        i += 1
        env.process(aviao(env, 'Airplane %d' % i, aeroporto))

''' MAIN'''
# Setup and start the simulation
print('===== aeroporto =====')
random.seed(RANDOM_SEED)  # This helps reproducing the results

# Create statistics object
simulacao = Simulacao()

# Create an environment and start the setup process
env = simpy.Environment()
env.process(setup(env, QTDE_PISTAS,QTDE_PONTES,QTDE_TANQUES, TEMPO_ABASTECIMENTO, TEMPO_POUSO, TEMPO_DECOLAGEM,TEMPO_DESEMBARQUE, A_INTER))

# Execute!
env.run(until=TEMPO_SIMULACAO)

# Report stats
simulacao.report()