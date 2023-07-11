function [tiempo, v] = Trapezoidal(TR, t0)
global a dt v0;             % Aceleracion  y tiempo de muestreo
v0 = v0/3.6;           % Velocidad inicial
Vo = TR(1)/3.6;        % Velocidad objetivo  en m/s
T = TR(2);             % tiempo de desarollo

tau = abs(Vo-v0)/a;    %Tiempo de aceleracion 
acc = sign(Vo-v0)*a;
tiempo = 0:dt:T;
N = length(tiempo);
v = tiempo-tiempo;

for k=1:N
 t = tiempo(k);  
    %Tramo-1
    if (t < tau)
      v(k) = v0 + acc*t; 
    
    %Tramo-2
    else (t>=tau & t<=T)
      v(k) = Vo;
    end

end
v0 = 3.6*Vo;
tiempo = tiempo + t0;
end