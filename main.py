# coding: utf-8
import simpy
import random

#Variavéis da Simulação
RANDOM_SEED = 42

TEMPO_POUSO = 1 #EM MINUTOS
TEMPO_DECOLAGEM = 2
TEMPO_ABASTECIMENTO = 3
TEMPO_DESEMBARQUE = 1

A_INTER = 5 #Create a airplane every [min, max] seconds
TEMPO_SIMULACAO = 120 #em segundos

QTDE_PISTAS = 1
QTDE_PONTES = 2
QTDE_TANQUES = 1

PROB_ABASTECIMENTO = 0.5

class Simulacao:
    def __init__(self):
        self.num_chegadas = 0  # self.num_arrivals = 0
        self.num_pousos = 0 # self.num_complet = 0
        self.num_abastecimentos = 0 # self.num_refuel = 0
        self.tempo_total_abastecimento = 0# self.num_refuel_time = 0
        self.num_decolagens = 0# self.num_departures = 0

    def new_chegada(self):
        self.num_chegadas += 1

    def new_abastecimento(self, time):
        self.num_abastecimentos += 1
        self.tempo_total_abastecimento += time

    def new_decolagem(self):
        self.num_decolagens += 1

    def new_pouso(self):
        self.num_pousos += 1

    def report(self):
        print ('\n*** SimPy Simulation Report ***\n')
        print ('Total Simulation Time: %.4f' % TEMPO_SIMULACAO)
        print ('Total Arrivals: %d' % self.num_chegadas)
        print ('Total Departures: %d' % self.num_decolagens)
        print ('Total Refuels: %d' % self.num_abastecimentos)
        a = float(self.num_chegadas) / (TEMPO_SIMULACAO)
        d = float(self.num_decolagens) / (TEMPO_SIMULACAO)
        # vazao da pista
        x = float(self.num_pousos) / (TEMPO_SIMULACAO)
        # vazao do servico de abastecimento
        xr = float(self.num_abastecimentos) / (TEMPO_SIMULACAO)
        # vazao da pista de decolagem do aeroporto
        xd = float(self.num_decolagens) / (TEMPO_SIMULACAO)
        s1 = (TEMPO_POUSO) / float(self.num_pousos)
        s2 = float(self.tempo_total_abastecimento) / float(self.num_abastecimentos)
        s3 = (TEMPO_DECOLAGEM) / float(self.num_pousos)
        u1 = s1 * x
        u2 = s2 * xr
        u3 = s3 * xd

        print ('Media de chegadas: %f' % a)
        print ('Media de saidas: %f' % d)
        print ('Throughput da pista de pouso: %f' % x)
        print ('Throughput do reabastecimentos: %f' % xr)
        print ('Throughput da pista de decolagem: %f' % xd)
        print ('Tempo medio de servico de entrada: %f' % s1)
        print ('Tempo medio de servico de saida: %f' % s2)
        print ('Tempo medio de servico de reabastecimento: %f' % s3)
        print ('Utilizacao do sistema de chegadas: %f' % u1)
        print ('Utilizacao do sistema de reabastecimento: %f' % u2)
        print ('Utilizacao do sistema de saida: %f' % u3)

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

    '''Simulando pedido de pouso, falta colocar requisição de ponte'''
    with aeroporto.pistas.request() as request:
        yield request
        print('%s enters the airport at %.2f. Wait: %.2f' % (nome, env.now, env.now - tempo_chegada))
        yield env.process(aeroporto.liberar_pouso(nome))
        simulacao.new_pouso()

    with aeroporto.pontes_desembarque.request() as request:
        yield request
        print('%s requisita finger at %.2f. Wait: %.2f' % (nome, env.now, env.now - tempo_chegada))
        yield env.process(aeroporto.liberar_ponte(nome))
        simulacao.new_pouso()

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
        print('%s sai do airport at %.2f. Wait: %.2f' % (nome, env.now, env.now - tempo_chegada))
        yield env.process(aeroporto.liberar_decolagem(nome))
        simulacao.new_decolagem()

    print('%s leaves the airport at %.2f. Service time: %.2f' % (nome, env.now, env.now - start))

def setup(env, qtde_pistas,qtde_pontes,qtde_tanques,tempo_abastecimento,tempo_pouso,tempo_decolagem,tempo_desembarque, a_inter):

    aeroporto = Aeroporto(env, qtde_pistas,qtde_pontes,qtde_tanques, tempo_abastecimento, tempo_pouso, tempo_decolagem,tempo_desembarque)

    #Cria, incialmente, 4 aviões
    for i in range(4):
        env.process(aviao(env, 'Aviao %d' % i, aeroporto))

    #Vamo botar mais avioes enquanto esta simulacao ocorre Create more cars while the simulation is running
    while True:
        yield env.timeout(random.randint(a_inter-4, a_inter+4))
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