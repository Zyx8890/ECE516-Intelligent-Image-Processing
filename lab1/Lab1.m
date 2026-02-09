cams = [1,2,4,8,16,32,64,128,256,512];
set(gcf, 'PaperPositionMode', 'auto');

% create a cell to hold pictures
PPM = cell(1, numel(cams)); %numel() = python len()

for i = 1:numel(cams)
  filename = sprintf("ECE516cam%03d.ppm", cams(i)); % %d = int, 03 = 3digits 0 padding
  PPM{i} = imread(filename);
end


PPM_G = cell(1, numel(cams));
for i = 1:numel(cams)
  PPM_G{i} = double(PPM{i}(:,:,2)); %extract green channel
end

cpg = cell(1, numel(cams)-1);
for i = 1:numel(cams)-1
  cpg{i} = comparagram(PPM_G{i},PPM_G{i+1});
end
clf

for i = 1:numel(cams)-1
    subplot(1, numel(cams)-1, i);  % 1 row, 9 columns, i-th subplot
    imshow(cpg{i});
end
print comparagrams.pdf

cpsum = zeros(256, 256);
for i = 1:numel(cams)-1
    cpsum += cpg{i};
end

clf

%plot comparasum with best-fit line
imshow(cpsum);
hold on;

[r, c] = find(cpsum > 0); %get the indices of cpsum > 0
p = polyfit(c, r, 1); %p is a vector that y=p(1)x + p(2)

x = 1:256;
y = polyval(p, x);
plot(x, y, 'r', 'LineWidth', 1.5);
title(sprintf('Slope = %.3f', p(1))); % %f = float, .3 = 3digits after decimal
hold off;

print comparasum.pdf
