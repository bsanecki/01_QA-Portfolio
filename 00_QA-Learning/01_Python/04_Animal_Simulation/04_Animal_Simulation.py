import random
import math
import matplotlib.pyplot as plt


class Zwierze:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.historia = [(x, y)]  


class mysz(Zwierze):
    
    def __init__(self, x, y, nora_x, nora_y):
        super().__init__(x, y)
        self.nora_x = nora_x
        self.nora_y = nora_y
        
    def chodzi(self):
        dx = random.randint(-1, 1)
        dy = random.randint(-1, 1)
        self.x = max(0, min(100, self.x + dx))
        self.y = max(0, min(100, self.y + dy))
        self.historia.append((self.x, self.y))
    
    def wracaj_do_nory(self):
        self.x = self.nora_x
        self.y = self.nora_y
        self.historia.append((self.x, self.y))
        

class kociak(Zwierze):
    
    def __init__(self, x, y, pudelko_x, pudelko_y):
        super().__init__(x, y)
        self.pudelko_x = pudelko_x
        self.pudelko_y = pudelko_y
        
    def chodzi(self):
        dx = random.randint(-5, 5)
        dy = random.randint(-5, 5)
        nowe_x = self.x + dx
        nowe_y = self.y + dy
        
        odleglosc = math.sqrt((nowe_x - self.pudelko_x)**2 + (nowe_y - self.pudelko_y)**2)

        if odleglosc <= 100:
            self.x = max(0, min(100, nowe_x))
            self.y = max(0, min(100, nowe_y))
        
        self.historia.append((self.x, self.y))
        
    def wraca_do_domu(self):
        self.x = self.pudelko_x
        self.y = self.pudelko_y
        self.historia.append((self.x, self.y))
        

class kot_przecietniak(Zwierze):
    
    def __init__(self, x, y, pudelko_x, pudelko_y):
        super().__init__(x, y)
        self.pudelko_x = pudelko_x
        self.pudelko_y = pudelko_y
        
    def chodzi(self):
        dx = random.randint(-10, 10)
        dy = random.randint(-10, 10)
        self.x = max(0, min(100, self.x + dx))
        self.y = max(0, min(100, self.y + dy))
        self.historia.append((self.x, self.y))
        
    def wraca_do_domu(self):
        self.x = self.pudelko_x
        self.y = self.pudelko_y
        self.historia.append((self.x, self.y))
        

class kot_leniuch(Zwierze):
    
    def __init__(self, x, y, pudelko_x, pudelko_y):
        super().__init__(x, y)
        self.pudelko_x = pudelko_x
        self.pudelko_y = pudelko_y
        
    def chodzi(self):
        dx = random.randint(-10, 10)
        dy = random.randint(-10, 10)
        self.x = max(0, min(100, self.x + dx))
        self.y = max(0, min(100, self.y + dy))
        self.historia.append((self.x, self.y))
        
    def wraca_do_domu(self):
        self.x = self.pudelko_x
        self.y = self.pudelko_y
        self.historia.append((self.x, self.y))



def odleglosc(z1, z2):
    return math.sqrt((z1.x - z2.x)**2 + (z1.y - z2.y)**2)

mysza1 = mysz(50,50,45,45)
mysza2 = mysz(10,10,0,0)

kociak1 = kociak(20,20,20,20)
kot_przecietniak1 = kot_przecietniak(30,30,30,30)
kot_leniuch1 = kot_leniuch(40,40,40,40)


def spotyka_mysz_kociak(self, mysz):
    dist_od_pudelka = math.sqrt((self.x - self.pudelko_x)**2 + (self.y - self.pudelko_y)**2)
    if dist_od_pudelka <= 50:
        mysz.wracaj_do_nory()
    else:
        self.wraca_do_domu()
kociak1.spotyka_mysz = spotyka_mysz_kociak.__get__(kociak1)

def spotyka_mysz_przecietniak(self, mysz):
    mysz.wracaj_do_nory()
kot_przecietniak1.spotyka_mysz = spotyka_mysz_przecietniak.__get__(kot_przecietniak1)

def spotyka_mysz_leniuch(self, mysz):
    if random.random() < 0.5:
        mysz.wracaj_do_nory()
kot_leniuch1.spotyka_mysz = spotyka_mysz_leniuch.__get__(kot_leniuch1)



for t in range(100):  
    mysza1.chodzi()
    mysza2.chodzi()
    kociak1.chodzi()
    kot_przecietniak1.chodzi()
    kot_leniuch1.chodzi()
    
    for mysz_obj in [mysza1, mysza2]:
        for kot_obj in [kociak1, kot_przecietniak1, kot_leniuch1]:
            if odleglosc(mysz_obj, kot_obj) < 4:
                kot_obj.spotyka_mysz(mysz_obj)



def rysuj_sciezki(myszy, koty):
    plt.figure(figsize=(8,8))
    

    for m in myszy:
        xs, ys = zip(*m.historia)
        plt.plot(xs, ys, color='gray', label='mysz')
    
    
    for k in koty:
        if isinstance(k, kociak):
            kolor = 'blue'
        elif isinstance(k, kot_przecietniak):
            kolor = 'orange'
        elif isinstance(k, kot_leniuch):
            kolor = 'green'
        else:
            kolor = 'black'
        xs, ys = zip(*k.historia)
        plt.plot(xs, ys, color=kolor, label=type(k).__name__)
    
    plt.xlim(0, 100)
    plt.ylim(0, 100)
    plt.xlabel("x")
    plt.ylabel("y")
    plt.title("Ścieżki zwierząt w ogrodzie")
    plt.grid(True)
    plt.show()



myszy = [mysza1, mysza2]
koty = [kociak1, kot_przecietniak1, kot_leniuch1]

rysuj_sciezki(myszy, koty)
