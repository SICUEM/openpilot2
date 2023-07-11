%************* Datos de un Tramo   **************
% TR = [V T]
% Se asume una acelaracion predefinida [a: m/s^2] en valor absoluto
% V: Velocidad objetivo en [km/h]
% T: Tiempo de desarrollo [s]
clear all
close all
global a dt v0;   % Aceleracion [m/s^2], tiempo de muestreo en [s] 
                  % Velocidad inicial en [km/h]
a = 0.5; dt = 0.25;

v0=0; 
TR1 = [v0 10]; 
TR2 = [15 30];    
TR3 = [0 30];   
TR4 = [25 30];   
TR5 = [30 30]; 
TR6 = [0 20]; 

t0=0; 
[t1 v1] = Trapezoidal(TR1, t0);
t0 = t0 + TR1(2);
[t2 v2] = Trapezoidal(TR2, t0);
t0 = t0 + TR2(2);
[t3 v3] = Trapezoidal(TR3, t0);
t0 = t0 + TR3(2);
[t4 v4] = Trapezoidal(TR4, t0);
t0 = t0 + TR4(2);
[t5 v5] = Trapezoidal(TR5, t0);
t0 = t0 + TR5(2);
[t6 v6] = Trapezoidal(TR6, t0);

t = [t1 t2 t3 t4 t5 t6]';
v = [v1 v2 v3 v4 v5 v6]';
Data = [t v];
plot(t, 3.6*v); 
ylabel('Vel. (Km/h)')
xlabel('Time (s)')
grid on

writematrix(Data, "../controls/tests/perfil_trapezoidal.csv");
