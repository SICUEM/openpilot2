figure
t=A(:,1)/1000;
vego=A(:,2);
hud=A(:,3);
vpid=A(:,4);
vego_raw=A(:,5);
% ----- vego VS. vpid
figure()
%plot(t,vego,t,hud,t,vpid)
plot(t,vego,t,vpid)
hold on
grid on
ylabel('Velocity (m/s)')
xlabel('time (s)')
%legend('v\_ego','hud','v\_pid')
legend('v\_ego','v\_pid')

% ----- vego VS. vpid VS. vego_raw
figure()
plot(t,vego,t,vego_raw,t,vpid)
hold on
grid on
ylabel('Velocity (m/s)')
xlabel('time (s)')
legend('v\_ego','v\_ego\_raw','v\_pid')