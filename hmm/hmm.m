trans = [0.5,0.5;
      0.5,0.5];
emis = [0.4, 0.1, 0.5;
   0.1, 0.5, 0.4];
% [seq,states] = hmmgenerate(20,trans,emis);
% seq = [1,2,2,3,3,2,3,1,3,1,3,3,3,1,2,3,2,1,2,3];
seq = [3, 1, 1, 3, 2, 3, 2, 2, 2, 3, 2, 2, 2, 2, 2, 3, 3, 1, 1, 2];
[estTR,estE] = hmmtrain(seq,trans,emis);
