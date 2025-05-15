#!/usr/bin/env python
# coding: utf-8

# In[20]:


get_ipython().system('pip install qiskit')
get_ipython().system('pip install qiskit-aer')


# In[21]:


from qiskit import QuantumCircuit, transpile #Importujemo iz Qiskit biblioteke-Textbooka koji koristi Qiskit SDK
from qiskit_aer import Aer
from qiskit.visualization import plot_histogram, plot_bloch_multivector
from numpy.random import randint
import numpy as np #za rad sa matricama


# In[22]:


np.random.seed(seed=0) #Da bismo generisali pseudo-slučajne ključeve, koristićemo funkciju randint iz numpy.


# In[23]:


n = 30 #Velicina stringa nasumicnih bitova


# In[24]:


## Korak 1
# Alice generiše bitove koje zeli da posalje Bobu
alice_bits = randint(2, size=n)
print(alice_bits)


# In[25]:


def encode_message(bits, bases): #Funkcija encode_message u nastavku kreira listu kvantnih kola, od kojih svako predstavlja jedan kubit/jednu enkodiranu vrednost u Alisinoj poruci:
    message = []
    for i in range(n):
        qc = QuantumCircuit(1,1) #Kreiramo kvantno kolo sa jednim klasičnim bitom i jednim kubitom -- kvantni i klasičan registar.
        if bases[i] == 0: # Pripremamo kubit u Z-bazi, dakle enkodiramo klasičan bit kroz Z bazu u kubit u toj bazi |0>,|1>/ Ako je baza gore definisana nasumično 0 i bit je 0 pređi dalje.
            if bits[i] == 0:
                pass 
            else:
                qc.x(0) #U suprotnom primeni NOT odnosno X kolo=invertor na stanje prvog kubita u šemi. Jer za 0 nema potrebe to je generalno/default stanje kubita u šemi. 
        else: # Prepare qubit in X-basis, ako je bit 0 a baza 1 onda primeni Hadamardovu kapiju na stanje prvog kubita --> |+> ili ako je baza 1 i bit 1 isto primeni Hadamarda na prvi kubit --> |->
            if bits[i] == 0: 
                qc.h(0)
            else:
                qc.x(0)
                qc.h(0)
        qc.barrier()
        message.append(qc) #Ako bit koji hoćemo da enkodiramo ima vrednost 0 onda i kubit ima stanje |0> a ako je bit 1 onda primenjujemo X na stanje prvog kubita u semi da dobijemo vrednost |1>
    return message         # Jer se preslikavanje u Z bazi vrsi 1:1. Dok se za X bazu vrsi transliranje iz Z u X preko Hadamardove logicke kapije.


# In[26]:


## Korak 2
# Alice kreira niz da bi pokazala koji kubiti
# su enkodirani u kojoj bazi: za Z bazu koristimo u ovom slučaju 0-->|0>,|1> computational basis, a za X bazu koristimo 1-->|+-> basis 
alice_bases = randint(2, size=n)
message = encode_message(alice_bits, alice_bases)
print(alice_bases)


# In[27]:


print('bit = %i' % alice_bits[0])
print('basis = %i' % alice_bases[0])


# In[28]:


message[0].draw()


# In[29]:


message[1].draw()


# In[30]:


def measure_message(message, bases):
    backend = Aer.get_backend('aer_simulator') #Aer simulator funkcija simulira rad kvantnog računara bez šuma.
    measurements = []
    for q in range(n):
        if bases[q] == 0: # merimo vrednost u Z-bazi
            message[q].measure(0,0)
        if bases[q] == 1: # merimo vrednost u X-bazi / dupliramo Hadamarda da bi vratili kubit iz superpozicije u prvobitnu vrednost tog kubita--> ako je q=|+> znaci da je na pocetku 0 a ako je q=|-> onda 1
            message[q].h(0)
            message[q].measure(0,0) #Meri vrednost collapsuje ili prevodi vrednost sa 1 kubita u kvantnom registru u na prvi bit u klasicnom registru.
        aer_sim = Aer.get_backend('aer_simulator')
        result = aer_sim.run(message[q], shots=1, memory=True).result()
        measured_bit = int(result.get_memory()[0]) #Vracamo i belezimo rezultate merenja i stavljamo ih u niz bitova
        measurements.append(measured_bit)
    return measurements #vracamo merenje za pojedinacne kubite koji pristizu Bobu i pamtimo ih u bob_results


# In[31]:


#Korak 3 Bob proizvoljno (kkoristeci neku od X ili Z baza) meri vrednosti pojedinacnih kubita i cuva tu informaciju
bob_bases = randint(2, size=n) #Bob kreira svoje baze koje ce koristiti za merenje vrednosti poruke - kubita koji pristize od Alise
print(bob_bases)
bob_results = measure_message(message, bob_bases)


# In[32]:


message[0].draw()


# In[33]:


print(bob_results)


# In[47]:


def remove_garbage(a_bases, b_bases, bits): #Ovu funkciju koristimo da bi eliminisali nepotrebne baze odnosno one koje se nepoklapaju a iz toga zakljucujemo da su sanse za dobijanje istog bita sa strane primaoca poruke male.
    good_bits = []
    for q in range(n):
        if a_bases[q] == b_bases[q]:
            #Ako oboje koriste istu bazu, dodaj ovo listi 'dobrih' bitova
            good_bits.append(int((bits[q])))
    return good_bits


# In[48]:


#Korak 4 uklanjanje pogresnih baza samim tim i bitova
alice_key = remove_garbage(alice_bases, bob_bases, alice_bits) #Kreiramo Alisin kljuc
print(alice_key)


# In[49]:


bob_key = remove_garbage(alice_bases, bob_bases, bob_results) #Kreiramo Bobov kljuc
print(bob_key)


# In[50]:


def sample_bits(bits, selection): #Kreiramo funkciju za proveru uspesnosti protokola u komunikaciji, a to radimo proverom delova Shifted Key-a odnosno odredjenih bitova iz liste dobrih bitova.--OneTimePad 
    sample = [] #ovde dodajmeo uzete elemente iz liste.
    for i in selection:
        # koristimo np.mod da bi bili sigurni da je bit koji samplujemo uvek u opsegu liste. 
        i = np.mod(i, len(bits))
        # pop(i) uklanja element liste pod indexom 'i'.
        sample.append(int(bits.pop(i)))
    return sample


# In[51]:


#Korak 5 kreiranje uzorka i finalizacija kljuca
if len(alice_key) == 0 or len(bob_key) == 0:
    print("Greška: Ključevi su prazni. Nema dovoljno podudaranja baza.")
else:
    sample_size = 3 #Dajemo velicinu uzorka za proveru
    bit_selection = randint(n, size=sample_size)#F-ja uzima parametre n-bitova-odnosno Bobov i Alisin kljuc za duzinu od vrednosti velicine uzorka sto je = 3 u ovom slucaju 
    
    bob_sample = sample_bits(bob_key, bit_selection)
    print("  bob_sample = " + str(bob_sample))
    alice_sample = sample_bits(alice_key, bit_selection)
    print("alice_sample = "+ str(alice_sample)) #Ispisujemo vrednosti uzoraka i poredimo ih, ako nema greske vece od 25% pri koriscenju istih baza za encodiranje i merenje/dekodiranje poruke onda znaci da je protokol uspesan i  da nije bilo prisluskivanja


# In[52]:


bob_sample == alice_sample #Vidimo da je protokol 100% uspesan


# In[53]:


print(bob_key)
print(alice_key)
print("key length = %i" % len(alice_key)) #Ispisujemo vrednosti kljuceva i duzinu Alisinog kljuca u decimalnom zapisu %i=%d 
#Ono sto je ostalo je kljuc koji mogu da koriste za enkripciju poruka. A ove vrednosti iz uzorka izbacuju iz kljuca jer vise nisu tajna, pa je kljuc umesto od 7 sada od 4 bita.


# In[54]:


#Za simuliranje presretanje poruke moguce je koristi sledeci kod:
# Interception!
#eve_bases = randint(2, size=n)
#intercepted_message = measure_message(message, eve_bases)
#print(intercepted_message)
#U tom slucaju bi Alisa i Bob dobili drugacije vrednosti bitova uprkos koriscenju istih baza za merenje i enkodiranje, sto bi znacilo da je neko Eva prisluskivala razmenu putem kvantnog kanala
#bob_sample == alice_sample --> False, a to znaju nakon sto uporede uzorke kljuca i ako je greska veca od 25% onda se smatra da je komunikacija opstruisana, dok se manja greska moze prepisati smetnjama pri radu samog kv. racunara ili nekim drugim smetnjama u samom kanalu prenosa


# In[ ]:




