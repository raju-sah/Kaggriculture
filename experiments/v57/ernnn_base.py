"""Lizs (Elo 2522) Backbone: 6C/4S/7G + Closed-Loop Weed Repair + Market Impact Slot Ordering + Step 630 Clearance + Late-Collision Terminal Overlay + Full Seat 1 Normalization."""

import base64
import json
import sys
import types
import zlib


def _lizs_package(name):
    module = sys.modules.get(name)
    if module is None:
        module = types.ModuleType(name)
        module.__file__ = "<bundled-package:" + name + ">"
        module.__package__ = name
        module.__path__ = []
        sys.modules[name] = module
    return module


def _lizs_load(name, source):
    parent, _, child = name.rpartition(".")
    if parent:
        _lizs_package(parent)
    module = types.ModuleType(name)
    module.__file__ = "<bundled:" + name + ">"
    module.__package__ = parent
    sys.modules[name] = module
    exec(compile(source, module.__file__, "exec"), module.__dict__)
    if parent:
        setattr(sys.modules[parent], child, module)
    return module


_LIZS_MODULES = json.loads(zlib.decompress(base64.b85decode(
(
    'c-rlKiFO-DlHjkD<(=1n1VA9=tJ#L%&=PIySu(YhJiR?69#jMhWR1Wo7*&u&YxM6MM;?(!6#&Yf+3AI6+9oP9Bd^HF$T&aTtEQ`b'
    'SyzL%hX<2YxvsOxO?FeRZYNciuBO-bj*@%xRe6(4Ci8W@US*R>lHV-LRh^_oQPydlmqm3^sBhD9d3#a3IDYvu86_Vs?#<KHO}4rK'
    'DCZaV@bksJaWA>JcbyiqiayiNn{@RitNHiGi(;0|lU24{q_>l0xyYxtopeh5bdN5I1pdJas-(O$U-6%+&X&;iO<r_v()XQVFUgA<'
    'D-Eu)x^r<4%P;Qrl3_O~SMcv{FIi-TfuHn~gRX_P%3#U`&1x{qvL*hZ>z*U1F+#z4sYa>+kL{v>j_$oZ`0J$3RxqM;fvb5z|95&>'
    'WvjQedi}Ck+$Oq8QohYrF!L%|SJ^DNgp%tl0U$|wxuE(9@66z$xF}vh87%!GyU7aPizKgb%J36@qzizY!+I_=_*YRU<s7!{RxNH)'
    'uhMBYNRp?paVbE1w@R1L)i=E)O{VMB3R?7UvN}y}vRRqWdN|n>HvKwVCCl|C%n_ERs8{78d6(DMfIZ2ZqI{PZS2*a4qFgS^0=vzz'
    '^Sr*rG4ldIZ`+`ihgj;zO<G@L*+ud4<k_?1@1LE(mUnmuF7Ca2b$0ys?@!Lo{(&2Paqs!bv(sPHpHH9t%zyp;^z<43b@Jnn@P}^v'
    '>h$^Xt5Ys{e0+9x`byRR>Eu}b`NPTCtEbPN{`<)pwS%31ad!IT*T=6W-~VHB{L9nl$Ilq~AD{jmQCfEU@~4xN7yQwV;K$R`mnZy@'
    '1_LMH$7jF3n*9Cb>5o6XB3O~B9VLf@p&7TD<Wcfy@Rj{Y{kj#oTda3zzEQ77$-&^uU>)%5BlA_S2!0hHd2QT}a+P!mOzipb|CyYg'
    'Jvli;0&y^e9sKF!$>j0zi{r;nU;Tr=4S8$vj8BU7&1JUgyiFJDtcS-wT`%g<a4^(ozFyrP$@5x4IY5~&%CzQY>SSi`r`fVjI<Ib*'
    '*~w~Eu6oJ8VKM#PJqpge>dQIS3Vc2%3>@UuJTLM(>+tt(k}aytHZ+r{uCv)Boldi=>RguTYBs6z-!t9kb-I|th;2dg@L_W3^!ve%'
    'u0z#<O7#-`SGVUCw-niy4XyO&k9Pd&BEKpoM6ng^143Y_E+6RUX+6CrQnkq6W(n4YGrNYfuPMVSyGfTzMH>>>ntYblK;f3FY@WX#'
    'Xu5zP;jrgWGKvyjBtjoPs$E4g2E+)^26x3J^;{;2eKNv|v`a&7kM~mr&220Cf{o6{)ara}Ya(J{@i~JYW1ngS-_kWgr3w!|eAI}y'
    '%%(L>2dhvWH3!wDx(r2^U5y%0fbH_C?(m|xP2B1*8tj3}x-cT$vp{Yt8)Wa{ewcO6?VX&=0T7U2!11)W$~tDyeF3toJK~|7+v|NC'
    '9i%ShQJTJdAZjiM<D7t$s~N1Q+lB_n1u#fza(<*oIUai;H9z6O^q{z-)ot{ej-4aORqdfzuFC(QzUg!$*1@Go`01XD7hDfk@e1zt'
    'CugTG9=>>X{P+aO#ImgN8k)Vk&f(}}@3SdzU&&<#W6bD`@Q9p~@jn3Hm#ZB3n#}1$eZy`5?HT)ZZMBZ}n!|tIWVc6&VBm<7D~`?9'
    '!rg?Ly@ZQlOK17C?x@~0#|Qi4ble>P&AzERT|?>U@Dy)>M=4i%W=@<7M^uQNRoYEtS`g)MUA#j8EnqIgF)*C>JEA;t_|*<5J`>^b'
    'pCLqhJ`k!?%cBqqW}Po+eqsRhDS`mvLSo8A6{*U>P>&GrG$?Mm;_$TSjY2l`eJ@$VjX6=295yV28$MgXD*G(HB52eq`Hn|m)|f`&'
    '6p7uD5SS_e?^&!f`&Gk%ksFZb1a9nf4vZ+U(|J+VX)(=A_r0Wp_|Z%1HE`Zt8jKts(%!?3gMhWTg#jRT>xSoq9?qA8an~7A2b*<y'
    'WQE=U=pR3HhRL@h0Q#-mF1(28`+NEQ{C3>kyiT7dFLRhUY|>R;WXK5~4!-UsxY?4F0sB)f-U40;+V$-8@y{nu`q-I-ceMuGfEUNB'
    '>s6K|Q`oW<kVOR8S94(uz09D;WKmAv;2Q|IhZNveP_~fJn5g3J%#g3JM-cH1Mgdf*Tq1Vi$3ffH3asqW;qU526(t+jOC#Z}OU$+>'
    'Xe~rdAh<%+C^ZulP0dtH0PqX1go}H)dBB#t9qSv3kWx(~1fDG#U=l7|+#`fTJQH=gcuM^ffsmmq3F=_%RzX~VDjH+Y-+SdLJP6ap'
    'q^eizDLx{-XBW`MSHGT}1TQb=yLfy(KE+k}NOTcL=WPt0KKDy>4DkL&y!i!QzOmXfiFP=%9_?>8UKcAUI{gNA9qBnNw%=#G?ZrK='
    '2YaH(g?k$DAD;%q@j85H*~ijv>#XAI8_`<s<{{iCiY4`N;SsY82QI*^pJ?qP6?ojCee6kbkQp&iT8-v<%aM2Lc6$!KSJ}pcPxl)&'
    '|81R;q=U|_8i?0?RhEeOYCP`yx1Ut&n~q_M21Enk{P{#efu?o$WL;(iTE2z-g{W*GMAp^xe~yzvCfbfju2k~Cf^p?vy1HeUwJc}?'
    'OnX@Y(sqJ3<OvY?8)O~d!V$TIqi<wl)q1&H+?uDP7AN5pHM<EX3Rt!O9$wkVxir6g02?WIX2B{WAq?J!v>r&jaAA*<;b3Sm3h_t_'
    'xjtHEYE{0Y7mVrIc~FKd-I0r{L|E~$hhXNCBEc7Z0n#YX;lubSz#i}V6m)FsV>(@xD5(V^))7<=zcOJ4TGt)GzGtgWh`rPp*+;c_'
    'kzRGtIo2H~5BS8PAj*i9M8CIrwwO(jPF0K*{)uB+8V*>~*!CgAftUfUhUS5+kl-+saGt7N+w@cwnjy>%&Lk0oyUr6j71ih23Vs1A'
    'znY|P(|nP_vBY*iq<|dVwqdyvKs`E#O6a;mRK`+ecsyJcDc)>!Y;->)PpTph#bNLyq{HEk&XM6t(XJHvHpz~CP{d;hwnA_cJ)gs1'
    'wt|GnCnrxFVD1xC9_&y`^grTI<2dGsV!Q$3ILmXQSeXb^=6StCMgZH-mzsfLnHg0g9aua%r^<|&@p_l5EPdl(tU#&lWqG}gjn)Of'
    'bS7|j&sK1KH$$K&XGhHd5Pd8$zA9I6=c>}KZq~KuYr25jVlvCs4vQOj`^(O~&)k=;S|*mhqsU|qTgJtUY>wnFe!?q!`Kp!9uddrF'
    'ng?;XCFy0=!EW$L(q}*xF8=cX7|;8*+JUWh;8sH>46CJ3;gY3>X)n3NHU2$ca_hr!Pc;Tcw;L?A=3OQ%#gh_3Xt!QuBRC!90!}4-'
    '!DYVRW3}8g8@*bsGnX}bnJpGc_BMm3rInZ|%Kx`ydR><I)<wZ4K7>iLR<ec>`KXXLQUaJ!qi~<A(Mx~SChRmaziGw{w?!Z=P<2Fa'
    'Mjkk2VrGj1ZYa(%>S}<)Fjcj>T4Lu&z<hzO*AmXz8}}}u^#fEmV$qVv-n0112#>Ac${UL-uMzZ=nrb?%U&%@?O>ZLn#$(WLYUKR%'
    'mVMO1G$7t26dViLn#U=MBWa!kBPo8seRNrQUlajjH%-4CCBw}^HQduA!e#Mhi{1|4Q35r*-tbKDtcfrO;)!Zn5?XLS_s!@$(S!w~'
    '_oWe1-@yejK-?I;l=#Tee-8)=ST@l9MAThG1O^>u(lk=bT^IzyApGZkBDBGB8KHWtHZ4%BfRvVt^6Fq|9*G_RY5D+IHb|FfIMC_P'
    'bb3iYwh%q<<*TPa0PsfYtdMY3imWNZ0`!cK_*^5o4@Rk^diek0(;9)>`$*AEu?I>7;c9}Y)AJ*%f*uDq7q`<VEnNTyFuRRY370%r'
    'y5LfSKaUs$J=64D={W-R$rFONOW@(HV0jb>JzXPm<~2F;MK?|-8gY0+-b0E34APk@x0i2p*F4aX{R{R^Jtl6-x7nmF-=(XWklokm'
    '3eFJRU@Rb46H(H5UCp2t&RVqy`5dc%QQ8%%s6;ZRA7IW#i}dDlmI8PnzDEi17W6l>D({iV*l)y_+`_@qKlNWj!)VknUZUyTi+UfS'
    '92}ME@_NAc9E$$mi{aaf=7i(p<Rv|b-m{H>ImZm(yUhSjjx~S>0RU7=+-?H!%jwyxp9lhO2AVH85Wd?C;pOSC0>T3eAy8w9^P@Ec'
    'y`+F<1<@A^-91pGNhxqW38GQ16u0sd3#^OV@p<unoP36dm-QjRRiqKg48lceiC`M7Z-6PP^WTxNGj?VCpm%vpG*5Gx$WtK0t9%BG'
    'A{v}w6Qg6SuT!!CV;u{0pDJq(;s7si*{<&EgKzG_MZ&sKb45WqUmtwkLs${38-0fVDRtdDC|@<@!Q%E+itAu4qW@{?=}%Rdi(+k%'
    '^5LUzhoV?kPx;#qRK7-xB{U6xoaQ`GVs}>QyNSJ0j2@xuz6|iKXolTOoB<!TsUuzRac#4#vz^9SsJ%OQoFoLRdUn1Zj3q}3&w6|g'
    ';_J9Ul}U?aq%a+;5LM4Vqt6KR;O@;E*Zvs_ytR&-kE^ST)8Y?xPvgCdcV1;~VZ3{)Tb@e=!>ewsuH7*XCa&{_1^;dz$a~>peFx*h'
    '(V3+;fP#xa0z20#+OhY#Ve{q@P|vTKYm}YXi2*5Wh2Ov$@yIl1<aO;mWyDB)LAe?h6b{3pa3#Vz+h|Cs9$;UaY+Kz7-^p=wH!b{6'
    '$7laWtdMI9BI^kiuLn(%AFZYz$+qTcp;=vNLg%y|j=h?~PR^-#aMaERr>HxdD6?|r5iZjzGv*FA<;;^d9h0^VW|tJ{4c!06@?0z6'
    'rZAQ(ZOVyO<4fcc0I0Hjcen&?lE0NXehXva4BFu?a0ZA^AK*gO9FcwfqvY6pR<Z@>n-If&4Bn79@?AJCm*t@Y@{LRD#b~F8!wGY*'
    '-jM9*KYAEuM%5}{l+q6?S7fb?cdltT^uY8N>5e^{C3eJ_n|l@8aL1k<dFsaAc?$ruvx(DCe<N9W18%VW(GNJ5K5M+!D>xJt@IpwK'
    'uJaZAH6>RD^lMnb>4Wo8yn#`@V+*L`+J{EQ(`i*JQ&5uJD)A=bl9>@!yrHAW5@8>X6%eCDfWRQK;?bKf)?_JF!LjCX3p1{&E~jq>'
    'f6mH#d+skfEgBt|??%a2-wb1?@Gc{e2p=7SzsLSS=yybGg3QL@pE1e?8jdtp`$F-5T)M66ELl7sds&6IfbgJF(2R(g+bD?a$7CGE'
    '_Wn$Jf2O@Z)83zH@6WXNXWIKS?fsed{!Dv+roBJY-k)jj&$Rbv+WRx@{h9XuOnZN(y+705pK0&UwD)J)`!ntRnfCrndw-_AKhxfy'
    'Y46Xp_h;JsGwuDE_Wn$Jf2O@Z)83zH@6WXNXWIKS?fsed{!Dv+roBJY-k)jj&$Rbv+WRx@{h9XuOnZN(y+705pXtBKpXu;WO>P31'
    '4Fg4|rq4fnxUN<YFZ1GIR=iD?w{TAskF>YXDT;aeRXW!Q-RG9td&n5<B>+76Ila1C<<s?o%&Dq+J-ao&PRi@(?cu@TAW5(AGDg`g'
    'oI3O)KsF&mzXP?%d`MC<7w^AY<u$xAE()V!U?D9%*srr9L7oU-!l+6?SsRPK;7dtEo3BcCpu!*15}mH#l~<?}`rA5NXJpt2%mJ(='
    'N}=)C!*jcW-C5+9^dx|5wYo_c3wTwMmM&Y(VI9^f3GOb6`^oFqyfl+)QP$P#*L>9i40aNuuF1Qr!l7s)&*P;ge{-PFpaIIdqN!zc'
    '^3}xAtdi#p10o2<g0m<KlJzpQBFo9;iw@6pm7!P!v6mW?Q<xqk_F(Og(ASI?(d?gcj!{DV>3W59F<YR<8Yw4C2u6)J=?qp(ImW>T'
    'GwzY|$6UFV&FA?vPZu7xu!*WBo6B?s(}hK@U}t{LGV(sjYqTqcmayn0)O-Wa(*g&c;ag=*)<%~%c|{16uIe0j$akW9{rU~`3;Y0J'
    'dk$-itR3vuAMW4w;_T_;lgSUyPEXGg(o;V_KKuFP)#SzT+41w2(lyLDVRa6_?4cLc5SXnm@L#}X{k9@K+;H#>U2o+T|2phOJi9uN'
    'MEftP{WYu`-RPv(k?_9mMm)wkUkwd}!=VddIQYVa@Rfz&dbf2B4lS4ie<EMgMDij_S3EEQ$N0j*Qdkg=7=)cX1H>PXWNYON*O5&h'
    '9mXaRTSx73*EtZ2aBz6&O}b_D+Ci^#IF$4MvU%{Ld)Mo(b1)2c!uG0XAwP84OV5bVkxN(3cVv^SJ@D}9qc0g(v7ue{JhKsXqfjaF'
    '{t}#f_d#h|*Q;2+UB{~~U1lA8pd6vOh_aVHV&elKA#lX?ujD`Jt)^b--K75=e^=wvMkmH@N_r1kh90|8yn|Y@hWSNW;8r!%PVTp~'
    'LWBw1ks=QZ9S=u$h~-sdOI884H9Z)%HXbS+W+Mo7QrveB?FiC&+6$De(1(a}Ib2Nqrzlr&b>_d5Ndhn3LxvHIR8)PCd;?>>Z#P$z'
    '^+|`C+`n)9Ez=w>e`|EynWJ$I`ZO1Y6-Ts7KHywGTYV(+79*Kwu88io4x4fkVj3wJ8Wz-qey9eLFYYrQH(o>03r*jfzpcwUW3@$*'
    '34enHTwV+3)s3&^UXuN`&fz9q<?9=DBzk<`!nIUP_1~;S0zUN;#X?-de;bXKkp4JV5L*Zv>lfp-qX+h_9D-z+fq%+@wZn5K2LU@p'
    'a)gKafXmUU3DAGKq2&QJd>}yI*FZcarvNEN2k2nN-SZL4JR%%bznq1$VE!!R%5F1@{^nUokaoTMku48qVb1gWj$km9_!rpH8QW}-'
    'P+cQ;UQO^hsddzV!<S{bIBK%R3RT^%6kDuesQh*do3-F>je{{h=^gA0tg<w7jSMh9g6w?cm0+AV-`|?I32)FWy@7WJyzO;(27axx'
    'Fbs$rapFKQ2Kp^UF9J6r!yFzcXv9<77Yz@rkB=Dyg`Tae9Jxw0Aj4JPPdX|zgCYif_1|<3j4qFX=fr^>GG$a>G2d+OJK$n3GwLf{'
    'Eplk8g?sRjLTwDqs8nWT?9`<#vi?%J>MuvkU*$JIsnQ}V*Ohw54&<Ub3N9C`nk@<Y(v(nn4xx>xXF%XOsl-j6xQVsd+chx2P+Kt@'
    '(=+0d2$`ZrZ?3xQRyW|9*v1q^{bQA7o!2H}L8puW7&#`gKb$tT7xYcp5Fu}<WUp>}Mk*ai!L9<q;odcn;NI(nqhP(&(77m31heuw'
    '+6ETT_`ujmqKhe%*S<TizU<uLD$}_ZGIv~mZWCJ~7L=gtalu;RLu|0CGiEr0Dy!9{-lUjpt}d0b9xkfto&}@?<(b!z;#Qjmxs%Y?'
    '=II~VgnS%{jA7StmC-SaO2JT!K%7y6^jwNNtWCJ)irBcx5pz`NFi+Bz3@MY=LU2taJ;1`%EJ#?miU_lVv0e7ok(MP~Fk!wn(RP?3'
    'jz-h<(o6bEbL=7ymv*<cG>sdWN(#zFuBEmaY=gD7-aBVvjh1_OLlFm#P6R+krPqRKJ$6+yqj00;)1b!Lm52`bXNP;}`cYl{untA`'
    'o-84$Z8uyB##3HJ$4-u+jH6OvDK>KkNkNZjyBi_K@3irTd8qY#pn8b1nQhM!b<%haAMoG$S<-SmNu2Bmaap@2Ma!FxXq{oysaiQZ'
    '-@Aeb5$<ckf*QmG?Am@(1I=dQyRm7ekQ!DTE#@9-59M{+pg;6faQ^$!4E@}U+xG)0SNRpW9(vS5EEA2?>u`P3@vzWA6b;oODKY10'
    'IYPOX{xA(mixFJin-T8Epa<JRT|`jzvr%;TjpRhz9g#j*B8&Okbs43Kp{n6s218qA%QRov=xI-t189GaVFa)Wi;0yQhN~-Qr1#mZ'
    '504tS^zp*L$Z6ac+8uq8uvRsa@!d=_tF{)r1)3_5ZB@@$LBzvY-61rDeu1^xmUX2Qz2<wL;&r1K-)(tdYtJaBhtcGmbD}I1dP;u@'
    'KP@z>t)9EaltH^PlZygs)A3}p`IoHMCF9Vs!(PuBJd<(FPlY3Q?_Ump*J2zNja;O|GRfAVotz&&NOa5Li)g%KJMwR3^d@GqWX}%m'
    '7N^4K1KlOp?nJi}T*zwl4emm@oRkI7h<bWGa$Gq1AiN?)VKPqvb1>{izL-4(5JlZDi$0w)*q9P(T%wQwe)72zN6)-^k87cZgBK`2'
    'AbFxsp8kjmnNyZ`;XR(vBIOt)tR{m(ETA{@Ona7V?vYe=JTqmsN<jZoAw&2!$493;^V$@UT)6bO86vx<kVXk9AB^ZZ-{ZOsiWb=C'
    'YF(uBIqTGU3K))L4QsKUq9aZCyp>Du-d?iASSQ!YX#2zP2rwF+W%!?uv3s_#KB(fxm7mSBN6KdTmBx^;5ZC^;t(XShSdL<ZTgI)}'
    'u(J2doNgJ5ERkB5w-aLujis;{p7&FWruz<tM$Gf3_1&$E@t-Rae5-9dM|fiyrsg=QmMO5&d|ZH4OVOYZA6a#d;uFTPDZFX`y=r}j'
    '(4j#c?KE|x-lW>JlWnrJcxs-nD%FbgrYsM_I2cOAG|Q%JdLUqtUjeGEQLD?xiQ(Y$n0ii9RIX1KSz7QsG2~&60(9#BZxR}@u<wvp'
    'ef=8i0{z0BewzUWd;J<k|D;!i7n@SL!&9z=ryMKtDFmqnRsj(zYLu4YC@$0K8x%(&J#-`aG}tA2riZXdb}-r!9mg0{BLLr0nL-0J'
    '%9&^c>K}BQjR_SZd~n(vsq4@7FHW}|w#6NQ5RPmMo>eWm=$gEq@UJ3bsv>Rc-1|xJx5{u=8r(_SdXBBvVqovJF;@0GQDm7B@tQ5{'
    'x3OK{-e&!ewGeOUfOlDKqC5g}7wA61tEA^}t{C)6JF>pbbo3=3%{cNI;CKVu!%K*?j9D)9gbBR;o$zULQDT1iYCOww*-@h=O=?(C'
    'qG_DuH+kI00}7z5opBg=J^={dMRmGzUm%(hyo#DYH{0h1Orhw-a3S}`8>Z{spS#TyhJA>tP#pWWc*i_&c!+3_9>wmAHnQIA(Z#qB'
    'jho<bhD4mB3pFyGHbhp~8chOJahZp<s0{J-Yu;Qv<V~CBayL6-={ED;{%AzyfgR~@!Z_LPZsMHjZfH_lvUJA~4MP*~_S7T<fA=HQ'
    'gWKnYrgkb?o{%2vL3;7@^yjTZiWq*7U&Ped7{^OTRZ~y<nO)rb{@16^o=lu*EH9oN|MDsxe54`p8M~oGU++7FP)SsT7B89`IR|oF'
    'n4{gWO}`(5P=m}#E9$72k5~;$*^WF4Xz<Hx_i-C%2lQQe`eQ(sCHBiFO6;J?y3Ug&R@p=alC9i##5mSM_*~KzfZu3yghS|1U7Zof'
    '@)o}hFY03DKjtIQHu`o*OWsCjORlP3M{P1UUB!E*%AamU_ktLa?!V)F>^55tzdd|3ApUle71MH-t)giVPz8@>wP<Zw)kx5;;L$?u'
    '*b|H2P}4<O!RvlemP_-Z*<FxFwGa(6wMDAhV>ZfF6=rFjPJx|9<5^X~d{R~FTQ(}?(&OS*+ig;mua`0}fet_An_Pyu2cnq_JnKf+'
    'UeU8Z^o$9k=7F5L;QQm3ClfLPi5in0ei^Y4eH2R*@YS%vjuXu|1ItV_%=8Q{#TRWvdGJ-3w*bu;8*&T`RgQs|Kb^jqh#fG~`u_Om'
    '6J=bg*Ue7W8d1J@`tSdKJV7X`s?FaZV}%9nzCZi*m&ZR%UcOL<v|%59h%wvtAIE3EOkTb^Jv&iN)y~-(Xs7e|?Bw{l99a;r%qF-9'
    'W_9vv^7!}%4c}m&u)lqNdiv_8rze{`5C*5mXU|X0UQXETMvr~BKx@kAl*8fajr-&j8d_dzOjwWbc=kAA9NFdlzhlh00$O*Iq1y3g'
    '0(bsAzgqJZ)Ny{%49Hdq#;*sA^y)1ss_?;wqjB1hTUq(8c${HHj3f0_wIIvmLk{SD=#Cos;mdS^YoHlJ)eGvXzTgY(;vU9dp58i2'
    '03??6WS&vTu8R1jBgFv0u<?&`T6?n882f?!6#4Ch!Jxbnp>%H5cr=H|`%}W-Ay=ndmR&wC%7Dzdc=7@N{jq_&;V79wgv_Ssl#$4k'
    '@#vY+Iq6|xg~<o}_s8a^P(y&t-j;5;;jnnXtpih$k3aB#TLxzXZn|WpIojsNh?|X3H$QRO8^dkx9A~pBdCdL$AJ|@A8o1NJz|TED'
    'e4-XVee5|P=Jb4}-X{d_BNE<CAWgih2vEcSYA{+F*eq}BI?YAg#0C(XLM*!Q(Bt>k!V+*)iQUgIUru!mhi8`Ez@R7al$gxY+l~%S'
    'p$36fsv~+BBRL!^AotaOp#_<W_w+{M?ZB6o(g~r$N&}~=3DV`Bj@kzU&=gyj>cT1A175M?AAyWv3$bQa`?0b?g)#JD3<=M-$C!g0'
    '@oc?Z<Wq{wd`+=>nXFchMHaWht6m>F6Z}{oU_c$s%9$`K(>L_qlZ%i%)W^`7y|^yaF#JuB2H4aif_6Aa+Ig(pOPs(JWNWr0(^(Aa'
    'tgNjx6samYaBm?oHC;Oh#gFUa5E-8JebK97SiCLOE*3Ial2?N+@m%vAEIgJsK9Bm)!I%xp?sd_1+B!>hu(9V34GzI0yP;%JhvM6T'
    '`gS1pH-a#(|B0?ZA{XcBuyOI7CAc5X$|1Pip6S8An)hM{n7iMzLYvajx8$XM=f1>e?vag`K*!Q02D*=%G%qk58tsE9VP&OL)sPKK'
    '7oY{%aq__)3<hICGgQ=Eaq<D!SRPeNbA0L`?I$O~<E6D8+YvWa0<N{ONLivcm18WV#<DD%Mf<c0=J_HOOl*}c=4}*_2DGk2Nt{+Y'
    '>w5$N4cM;5uLx`E)q^i#HE;X9CSGaSJg+9=uz78x2Qo5JP1u=$x;HM*5WnjvO;uLQug*pL(WQ%;LOaygJDjl2$OjU-e!zc!WT}~4'
    'V2jFvbO(u}+UbSpOJTmgqQVZ{qcLCud8*qB89oKnoRAi{{$bhxSvwGg5JUu4)7%Pv45e!rDz)~983{7#RHw&hv=Lkxk-i&tIcr;Y'
    '6U27oY6B&iSe~^JAXMXk<C4R*wOimXms`PCRBMM$7*jDrqT;11Qf+i-PFPzHyxT*`3-n+=s@?+KkLJ#mlEkpIg3)$ZY8|qD!g`9>'
    'b40Df2OjE2^DY>>xi}dI`DNftQ(c_^#`4iDES``A7;Oxc{3eu$NWb3bjcOtZY6*$59uDn$+{l5XiWl`8%^PlV;+}U8AZTJ-Yn8su'
    '9O4C9ADP4<YSi(}BQC%(E5@8Yng?T?AGYylLYb0VwN@AzdN8RNiE`x|gCr^=E^nuN^DV;~g;nV$ReEpCr22)^L|=2;irl(_bt2{$'
    '!|!8nI9u$_eNM!X!+DTw64Ske%D#|}XYfTg^7d;5hZSFBt0%l5Y9S84=tduc3X-rU+D($U)q|od4eXQ7E^S-^rF+aft_|SGQ+dKV'
    'jo^PhNp2iQX{1aBzdraYhW_&yG(K-5{*MC$$35czi0_05Bl@@ZRdFRFO6aB~nu;%y<8}CnQL{Y3#AQS}#c(`!Eu4DW$OH5mIlsJ`'
    '4qlI(UtUcQ)kfZLnGi+%?Xy3l57C@DN0DUD5k60dqB`5SU&iw4g@a?x>dzWkEKNfDu;6%(d>K4mPI6uKeGpVM41<HV+3b&<o+AB3'
    ')i<PO^=C&fw?A(*2z}e(bcJdg9iGt%&8oFuVvHyDLDaYE3Vpuek*M9qIoj1Djylw@SNYWydf_0oDGC!Y30=p1?{U;qq{(~@J&;MI'
    '>7T++X(RgzEz>ay71O#ZNiPbUbh}(;1?$k!u=WzR{ckqHl#X<<zN~I5$}CaQ@Sz>7B*w2x-d$rPEe!9(?%^{n$|Iv7?Wap~qp;E('
    'APR;}?(x!o`3@nIw$RNxfs`VO`sbXA+&c02CJMTuej4`NSLvS=oym((G`vH6CO=Nn@D350JQ!aM?--+L7=$?*?i{6Q=!9t+?i#15'
    'c}2I3)YLkM?P4`KQ;<X0F<MjPiyyD)PYjCG94}}e4e9@rXh=AvPmOo9k4v<VOY}#^CF1Zq8T(u}BB9M5WO0)9AXJEI4mTAov2Lim'
    '@8k2Hgb5f7p;+7KTTn_tMAC%_7wQF^;1<Rk$q&k6!=qR|R+#-jX7%kl(mWkIB@#8o2QA0*V8kt@yVa=<sHu{@&&rIWoTsx{^1lv}'
    'D#hd#b!mbf7^$?EGYm)cUEq8ng17hv3Tjkh$aZ(tv$rfr_tx<h=$<OeQ__fCjVYQpsG0u>bjF{qpk$BOGk&{hi?f@XY=(}D6SZ@S'
    'q0sKCGKjcSR9<3S>in(yl|xNU-1F)bIY(C*&GD!vh?$e=b&0s|+EG|?(4?KTMi%gLX6q2!RZql3Dav=wH?5;pzpu+x{ySo+QOfq>'
    'CLbQgHd=Uyl#7)6nq)8tU2|_Ew3O(1Yd*^>5;4h2fBo{0H4BNMgd&=_<rEK0V+c_Vc+##bUi(?UF8lgHtYvT}@HoSI$+^BU9<UoY'
    'd0LVIID519*)Uu!6TTyp<Ov`0I=@jarfPLCI*_Jr1-x>JUv)wdqdPah)~z?~dkmnC=fBG8h=+G5KJ~xsD&f?47N&I9C78`!dN(^L'
    'Yf|8t)$cj?O>j~6g7eTbW9WL;2A*5B+cC;a-FAd(NU@<^D+!l*xaRYU?v?QJb556g11eF0&>E2V7USs<JaIY68_04Lh7)c)aa}LS'
    'i|q1W;#NnopfiFO8rcPMl5lSB#<#LzUoFaof`Xb&rY+657}4puMmt`<zcA&cRmjMZlLlr3?5(YRS{Bs5>I_NTfkkq!E*Z>U(^cSk'
    '?UA_eb>iHy4waN~G5yPP#9~YH-AVTB3`o^<KRSY4eZK}U;W)U>L@WRP9a(Y^RMJO&WL6=}F@2d;>Q2_Ry<3_5Q==E{yS$!WPo`y6'
    '$8Nd%_ussOS4^cZBEi2C&qseb>pmWPNt7x2j}2d90z@L=p-d0g_)G$l^)^?*6-ab=of$D{5My@|k22{LX#(OTXjI9%?HYS>?V+bc'
    'aUiyp;hFnlQ-wpXLg$fs8w#@S!TIPa;yC)<hcMjcQIs>&H^j(H!EC5!?jZBL+7)y1o&qqA#=>hJ%L*w5E)sCsF?z37oX)w)Jv%T*'
    '$*t8-@UC!jBacSj;u5J+MjsZTyS`?wkD10yqrSKH5tW$xM%F9PqmkRw7u;f`;5Hew4X<lH9cfv(G;Hg6)(P8G_L=P{OWY7>_i<S$'
    'KR{r{(4<)9)S<W~JQ19k2*&GbRh&~<mo@QYUO0C-Y3J7MB6)PtNH+7=z-=4b8y)~##vXoQL3wP9)gW=ajR{Ie($%d{BVooAC)f)T'
    'DK&Kp5nOX*BUB{m=w_c5)a=fFkG<q^%GriY&y5*lbTb()v!~-GN{x)xZ0QE!-Qq@{-K5R2hG#v;yr`FuoUzd+M5%j@U$Roi#upP_'
    'y*=s1a6XpCGx%FN2n5kbtz#G7Wcz@#y9b=D;N}LR$M$EFMOIwZ*By$t<e2)B#|8czk3G4xasX3J!l=*At;f+}sj8pSl1E@gek#xl'
    'I~f-V#%Q=t!B|~&Kw9XXMJ8VOlH2w=+Jf>6@3yDzR^teyZTwxRjMV!qo&CqUqI<&zul3A-R3P_svAj+dgBH+po%p^f60S{;M-@@s'
    'VPi+M#{#DoB48T6X+0A`Z^#?tg>M%j+?U!?cX8`n8CARMi5|^;#O)(i!|GNU3`N#nKazJC1KWmktSZ@!*SN2SrLkd(xxj9*?~0@Y'
    ')cm1pj#_FSpw6ocd~q?oRk8`n1LT5u2;c`pk4d3DzMm)snRg)*9(6HDw*uY`<3|(MNP%ZH>vE|%J4Nxd2dUWhkrG!qE>#N41@4;1'
    'g->|Z<%<^v*+j&$Z0YdRI(nPVm}O#v#3N7t5rL;=cK5B~MaNPNHypLNYpXug9?!fx>5#h+Izq})H)*RDIcy*+f)z81WwOI7E~7ON'
    'cQ*)}y=~C!Edpk9aO-H$?5gd;<Ve>lD)wFDTsK^sXl=xYOi`0O`_z*b^8Jo)V(g87_@#a219<_i?`C2o?9^J9PSfgoqE4REzU?G`'
    'ub%tQUp($F@;55GpP~JXzLeOPwnYoYL=uk5NT>g|ZlzP+q39T%CfE68PKH(ZW?km+0O<2Z&@vF;&SC3u2C#$LmGSDj)>#9WBoV5W'
    '+&jHR`7?^onU~hl5OZzCg#_vQU;pv&r>AEp(FmlQNKU?W+yND)C@wCH9f%!lxOJHBZ{3}5g|Dt&m7g&dt=a|!F4W<6Q^|a0Q^~{*'
    'jRM`>G|ip3kh!|}wU>!>CPu@HZ(Zze?V7P~=G_GGS?o&w8MLOGK7Ebf5X~&s2059}YZ+CXs^&_)1p8&2f9x~fq5MiZqO&wKN+snC'
    'Mg+_K9#|po!U1})T)oMNezpnfMr|^`n5BC_e@D)*o*%zUs$xcZU0u6%VK2@VqE_RAtdGRsz39D6Q9qRc@4G-x;^E)9KBqd{jBYw^'
    'yE7G#*1OM0#25K*Yoe$?_e7?W#`kz5MZF8%`^?V}9y#s1y3kzH@!4c-eFvu>`4rhchmlT{B6(KYN-623^Q_FRU5Z7tMaA?J;i`!9'
    'wT3Y&K6Au=E~HkiIw9V>mP|>`>rT(lu$c_|zH78YVip&TopM9|+EcGYxkKbA4;+q?WZ6dt!*Mh3_pd^p$Ce&vD9w1r5=f2kZQ>K-'
    'ER7-};bg8X*(bt_-TGBeChAd|*OLkRRUi3u0sUz?*`eBVc2D-@GEI3=bcAUQgu}ppkbq@^6y0x3d?Y%?+nIhk)7vl_;Fzd!GAn5='
    ')CoziS7;2kBCC0hV5h}0_qvgcDA=*4d*$lL2wKn2N$v{&8lzBQ<%op1x(afPapmO-P=tB;L3m=D@X@MW|A1=u4?fB`h&Vh7+Z|ze'
    'oPb(hl=Uq=FujoOTT#?l;ujIn+sun&Pe-)ZcF9Z}Zn;LD&y@?#1ln#G$tL9Sv|4(zo7qXfAKkX~z_ibl0QhRLHBm|d^4xDcj+!gW'
    'OOhH=au1G#j*n~lrV@E{od}zVRRafo?T;`RCe{|36!xC6DwG%Sv?+02BH<(Xc&R}7s6v55#cGj1U565ANDd~nAd{Qy27>~qL^Z0R'
    'ip!}}<OIqUkqtyQ@w0>o&4{aQvVHgxw@u2FZB!;3%nM)ec0Hzs3Rm@@ZR~3$1^7naX6h9>X_Dz3ekrUGFp0^8H-DnAqho?&^N5e!'
    'aR3bGw~fE9VwM`;DRRHkmH}+$hSa@&SE5LO@oo;&q2vYpxHp1?`^htkp6C0svl$xfDjTTvmBtL2hdyo#Kl0#)8)!H$&XUg$9{u$T'
    '9}+K5UyEt`T1*#*#n6ZgP~5!E(_lEP=Pw?UxWlo^OD`*woLpv<5f$g3uWX!^{uQA068gL@7c+njcVRx`i~R<c=xvs~%kj7c;tR4i'
    'ABD+oBmoeIq7&1Rxn8yL8odA@r_15B90bVdD&u#}&B6f_Wnwfp!-~f2#tLBywVq=bvH9}e>Ehn~(%$vLzSCvBMJ|j@*R#ojfr!>|'
    'lUv*|M!-%6c5du>Z{K4<4OuEaQX4jiQ$b;{6&mQtE?q=y>(8XSji#Fm^fT5LO=SG^lmT+YBX8Vy$WrI)o~;5ku9a@gRmYr1OW16#'
    'pl%U`5oSxAx0Yf{+*@e2P8Sn}Q~D}W$CkH4-%I{Q=YHSv(n4{#Xa0s<6uGWgM__Y%8B4d)a|CfVPh_>uEL)ab)9bfND2Gr6E#Ky='
    'vOvjsUmXWBxl8dmjl`ciE6Tjm@yPQUuA4rk&r!jO5`90eE0qrnUN|L++$lUbyg~cSlj+R9eb}f}JY4_A8OMN6Tf-X8>@}%IWZ<eK'
    'W|;fvU0NkK@Ir-emvC1mI$4r)m01OWzSLl_-<S0@Zho3`R<jDHqIgavVnLQ6a?|nNBPEKlD(<c2;z?JZtgeSJ+W`yk%ZKM>_*9)^'
    'QYe|#Qv<Qz?{?Sx_fcIn@)#8~bVAi_e~(2dYy)fsmn+4A?nIMRZ)&4ajm)8$MHM?=Tg$H0-RK)XyS~tp@SF6Fe0yPLNfe4@1w9l<'
    't<lGKA=02exd(8=J~T90?`swMK<VFV>xrg<2#|XQa^7@sIm<n!R6|EKq-3vOfB)-0v?tc<*B6CSi)d?TU|KJ;c}a{c%Yae6Kjnx<'
    '%36bzMFk#R#R$KCja;*ZhPHT|L!2~xFp84`_eUxJ(0yf*-;hcWedbWn1A8*B)oat_uD&R6I*NqxjQ&!QoK>kLS%=e0V9%8a2EHhC'
    'KRp_0%I+%gszT)=JcLXv2q3#x*R?T9Ag`J!nX+>*2cT>~B6v}VD4XOL>EfcGs0B$?LMLbhL7^OQBQWzYjGcUPifXNrJL<vH_^eM4'
    '={9dlibVl`l{Vu;pYzngv@vGvO{T_-Ngx(ktqC)<p_mz1`2y2VYQu|kvC7ifZJ+UVX3a$}Nd{OJP9jHW2(O@geyfs3!t0i=51QCD'
    'X1Rj~I_R=SOx|o{aPAPNVppNSrl1uh?R$zIr%@}*NFLhh0uT?q7ivD_&6btYJ7_nXO2_Y!3@MrKQE|5)pT1PF{7sC072`q0_E%9b'
    'Oj!Rfhj@WJJ_D$xtsh0>U>FIEA@WSvNEcr=rllB0(o%e*GDti-{^g189m6tkKn4!kG3@T(Ir$tZq9fkO3f#Tf5v5Q8@Yu*Rpr*7;'
    'YOY*_IV91-h!14FN@tc_CO2zhiSoq)r4BXmc=i<Q(C~OF759OEPFi}S)IqKR##cjKR4xGlFwvPT|N7u7txbAAxkQ?&OLRl6+{ZDK'
    'c{&Vro(mh0gMq1u!t=?_4K$Wd>T947$eIZQ5w9*xJ4@e8v>4tvLw@59w$0i^EG62%MXC*i(>D|IiPFZJWi{$O<U&w0a=D(*F^I32'
    '<d;^dH@OCaw<^mU17K*E9cSzc%)YRN$`U{o91I0axJlBf_QavW;Z_KKh8+DXpgs8RICAYNg%9uL`c_)|2v^6L_i%i-J>}zs?oe1O'
    '*^e#d%bh5h@EG1S8{WR}5ie#Kcv!6+Ufj+o2q)-@bv`2^1f%6$cRrgN#(eby8Njsugg6E|Qh{KN65N&qO`}%!(TC0#81{gWk|cxD'
    '=M@|Lw+1sHeSwte!GOYO299UoftQH8s-uwx$QyJ556dO-#~VD!qb}qzpEmZ?%qZ3%^OlY)OzaRTqqQ{}mA(T8kGx-y<tikLsxo0~'
    '+XdvQ-E`W{&c%&y0{=8x9CNya)38R$o(x4|nyZs;&mD#xF;M!l%Wyr6>RX3_nD`!vapz^xT`&~2+0N>ALQl0(#I#1!E9FB;zFR%l'
    'rqpxYRKH{`kBqq$VL^PT5z;m?e?{ww*^lH(#N9CkayK|-ZiV2@$gJ)ex;10RV4K@KdL~p10_SL)DK{$=vtXb-6bV^t&bn6qxoSM>'
    '@$*)^I$speT=Q&Ypdw8=V$@)htysGc?Iz5Nuka}R6t}AKT_>699yk#L{4FBaH%(B-o+He=h#L&<MbrfotM{a*C8k(P@bkdi^Ip=&'
    'uRiTj9dtq?zNq1t4;B5y`II%FTGy40i<xv|;bxGLY7IKwvq#4BB$7Ap+q}y0IVoie^!`)?ty1!U8Xw8H0Dn=DGF+F&U9>7&2WHkW'
    'jZKv6yN5J(y(bTPpBm%1F+}lh9c`EMtRb$l$m+CPcxB)3XXqOI{fobPuEm-RJLE?j+8lAH=6J$gFYJ)Cq-%~KBu4#UyXZt3W)OFR'
    'L@sK&!7jQJjwG<5By-X5MxGcoqUGYv)3GO<O>F|WWBiFo6eW(mn5DHL86HhgZ4Oi}y>@M?Sm&XDk1|gezA#Qznp!i6yGF8C1La`y'
    'tU4vC3((_%<L&gf^J<-z%baeFPxNYKI9?)NnkJX%jB2WsXX*R88XzM7uHXU)oRarCtzBz-w?_raUDmPJpJTykyJ-b%6`Txt>^*F-'
    's?5a5sq#qJ>*rw%5VKm}$RH*04AyvDDDiJB$)LxHY?GX^F*jpyFHcBPkxtP^krHuNoy#&^!3~xFp4pdhmDT6oYgj*ruhYfcCF&MH'
    'mqJ|}Hf7E0P}@G<Hu^8gyHjyXk!{(~Dw0BOQm1dSPBe=WPD=0|F@b>HT?A7opG_INJn{nUMayHp4JMOe&kwIj-3fY33Xjo7K(Ip8'
    '(zz3;?RU*llsLdAX}ach>y2Q$UY1MMH7Ot6pbb0%vjZxS#za}rtA`oI*0v6E%n3>_Ir-&&uSv}2hOqHB*H~HGk6t937d$xQ7*GSV'
    'U(L}OikQnAcmyF+S+Xt$&+YT)_%d4Mmup9je@wB$O`dXQO0{}S>8)9II7pIT3-X>LBY_3^wkdUkI%3&kiB6t1JG1G)YzY!Xj2-#n'
    '>EoY&eUYS9@(x7=@ZTqAr!OA9cy|2wgro1UGD#VEvaA~^1L`st$qy$dPxMG(Fh8X$6tKbcxFYoF*rk!eaFxw+^MZioAk|?;I(*h4'
    'shRS`>8g2molmdfA%hvwX)$%xsfbY$QRCmuN8^LEoLUibc8_8QG)NvA_oAT85<5oO_k26@%zF!e@J+IJ8s~<wS|Lwk#C>nhra@j<'
    'wnj`>%p=C&j4fk?{E}v>tiye-t&YzrOB0l9hDim?fEf?Rz+vC-$O@4hr8?gnYP?4=2B~W(N4e5Q7}zn^l$;Ipr9NpsMS*6QQe?}-'
    'th<U+Gjnl#ENngPvI48Fy-^pL!z}8#g;%#0`I$SE2ysE2L8ZK8^yE}rg4R1+uLScffMW3Az?>9b7I5IdUj2$G(!E6B&UcXu{P8I!'
    'GB@@p!do6?+!GsD!}`oSo8fyRQ39p!M&9x!8mumoo3YUuDa<@A#>SUHSBJ<DB^%)yo&U&U^*LvSYU^Cr4Wh6RA-2=@{o><;fR)zj'
    '0p0MN4v+K2aTZlW>I~7B>sH~i!YjNb==*#5{rq;^-Mr4kUvh$MY;o=^LnOooY+kTjMz5-TUB!Ojv@Tp0M%2dlG2V9SW!%Aa>2g39'
    'JP$|P&`Ua&mYGq6GM0@ERfMjj-(f*0U?(vA<Z@@i*K}jT0NNrJ^0^^NJ$m1xKI5(_21=7N3Jk+=bAelL^1uQJ+kZ|LBSw3LOPpY^'
    'MxZNIf@bgY1w2Gx7p_UjmKMrJkE|-{L1et`%wmXMZ9C2!Ps5(mN5o-)L|qa=9EH;62);RohCT0YW4Mt0wq`zwkD&x{IPPj8k3Wb<'
    '(U6-MC1wd{^VRK=ecXD&->ti$cQ2lYew*-H2lrjOMk+KjZDTppy_ZJw^Pu73@xXs_?69lIu&Pb{BlpkTdZ<0~FG4f=a4k9!Pcj24'
    'XVW<=?RIRuF>Y-1tsk!|-u;*l5=9ZCk?kzr$jS(`Lnnf9>&8&WdjlIk+{oBMVy~Bm&z$NvN^6_j{|`G)e+1E&1ixYZ#XVpTs3QNd'
    'kUq_{|E_dDc1k}_PS{%gVDRX0@HIZ#$_2a+`JH7BaHSu7)9Y+XCZ`yKVO3q{OSnWNI5s#>NfXU@pCqSzi@=Zm&AR3YEEY7b`E;?S'
    '2KZL(NpNhQRh0d5shD=^00!4rw*ia4YIL+D<5AMUxVaUWgFzDX?DX-^n2PmiEBfWTX1L_+2TJPdIe%<P7`*cxJ=<6Z51=nOoTD>G'
    'sj_wckizMZ_~RpgfQ`mxjY)zl&E(5OJOqUlJ-_S_TNjg;rM=`5mC-$YP@8R72!?CGqFP_}k`%D_(lwYCLtxh#v;okPB>Zqh3|=o('
    '%d;hn&f%nFEjeH~FJCm<fXUwLBq@MKB58d@5~b2a#che4AgyG1gIl{^vLgwGA$o{*lL?y_uPT!$B}|N>czm9B7;6z@#EBX9BJ<J#'
    'YF&O@$M>-!Ne|g^l(FbV-VsrnWGgK8mX4y<5h{sc2H{>r8LHWvqOX`ag?jyP0%*U5tL#i7dta|oOZ!8}F|(;rVys-x2>@w&7!*IQ'
    'OnKKRqr7F4HZq%b43>auqEOe3v!+xZ-zJYf1sB}wdb?;tTi?F|+;CG+$@r$dJn;y&+5}_h?B0I&{qT;9I9Rr_jsX_-*LMT0G|MsA'
    'bTVutM@yx;G4PH=UfU3A>)1PBk{iAbLn;XqTS-=90{ZGmL^1IN^{(Nw8_>=%glZwnK82<Gq%rcfvO8724mfyzx55=tU88wDn)N;;'
    'ABA^t<-lVWedREbD8+_j3AaOA8zh^`#bnZ+Gh5F;k~v#aGYi0oKW%Afl45B9%g1EH$o57AjXI{cK^yY#<)Mg~StE5NvB2J}cbk~s'
    'gCxu^V%Xuic0`U{{1!-;K$c5MC|vUcnfgN66MQx@V?S!XE&}de%-6AGFn-KBGB9>M7E$%&3b-2dAZnZrK&&M3uGU%XNx*fYn9w=1'
    'a>GM*CrDk*7eFuaoHyreWdDrR6P=IbK*E|Kx{YG@uLLX(^vL_|weSTpgtQMvv_fHocp2@Mh`{7hTc7Vrz#`^puCH+5jnZ?ef>2(@'
    'vpzN0$2Slg_IJ}3dGfg1kcSS1*u}u@zaU~6A)9aC?u7+Yj`;EDVD9Q_%XZCH3j1~kircNBM%rCRu^Xz1{S3XD*O1eueF6qR)9|T6'
    '%h&|~x4*7+U)AJE=IC&6&NT#cisHg6qG18GBdx$jlBXu7<;4?6LZVj5_7pYy!zPba3&b3?8?LNHXbe`-8qRRC`J9uD1mkh-HgI&&'
    '?t0p;B|b6N&QW9tp=YxF?P`Fxuz+yG1P7sl1KWpD!%TY(1AKSQR&8E#4y8SE=0UfWKuDKlpft%facZ=2iNNT#XrQC3=S=7G<iv>|'
    'J}qx<a^h7hApEoSG}CT-#%(sSO@I+s1{fL|M&Oag4GB8WE>NCys|`4M=(9_acz{6X3ks6Jp1bcdlDb2g1}DuS2A2I<rDVU=iD|8y'
    'IRnWFF<YSnngck=&qZH<9REeUr;u54$XqOb?`FkcAjgekn3DsJ3;OZLqqHU8MS|<g=d}Ofgf_t^Ka^m4n&pd5Xv^1?Ih^H%Abk<N'
    '>@-}SA%zfAcE`~7m%zShWpin-jGvhWoOljHjrT*(0TxeTY~YGi8oWw;6Pa?o6yiOq79{YiwD*#5upe!BMK%#R`Nh5o{D{2jX)zMA'
    'Bz@%vZlR6<NwB{59+rST&a}}^9ns~dw3t1HDLuz%HzYBoyWUvv?Y4xDA7e<K2Qp|CbAo*rYRtbD^%DvO?aD+`U-_(P$LnoG|CW)z'
    'jLYU|^DufY3ew_x9#}lKQ7}wrT}I}wUXwX1-KR`NJKoh7SbR#>_s9eRAk*RT*5-!M)W{LxuJ9Kn{fRK<!@I#SC@PeM?<T5k+qSY4'
    'YcO^&E1~TiJ_dJ_T8vM*aW>u^Ml99~1%715(h%`HymPh>f4<X|5(*~cBFN}n>1g28s6s_t-}kPJ2n~@{@T7)4PeSRB{EyIAZd4&6'
    '18t+n3mX-oDH7+Bt~~c(y55XUC$P~OY&*x>KNhQ_d=w3EcUB4Y*wr75vl^y{u$s4P#@BE$MFK^F8epgcv`MP%z<w}dP!670k+#7V'
    '-)EO`hk5l*)QNU8@+dkjvXX7#W4}k7jfgWb&gC1N$_0!1iTE_}A`NVErkC9*r1PQ_1aW0fDE^BZ;}0YB%-0JY8-^^{fk&!1lNBys'
    'Uck!{xfZzHl_)L9StTR3i(u`&s0gxI$mog^z3Algfwg#!$7c1ad-2E+S%V%sej^H5q(h*8_(;)EKYaY?)oO_2+7io^i!c&S-d1=!'
    'VOkQe@V>REt*PFziSn74wfEzALQ|zdSdG}=OB9bcz|mK8YbA`8)mkB&U1hBm0PV6BzDQfvN5%13V5p(2y-w>M&9dd9yd}1yx^7w+'
    '?KMB=V8HZF*i=`%?l!g1{_2D-I>Hau7Rj}Yf0#L!2(>n;0n%DsF-Cdm`(4U}MFEPNXt~&JB&W>9Jz({URva@ip|HGv5LCc8yNkTY'
    '_@0adDY8_@W@_Ein{t-L7btS}MF8Mb28nSGesd&Y%_(wgu>&gl+jUwIrcxMOy&*=0>_=asZ9!8g$9y9<L7SCw^1!*_Yz5_DAjxOI'
    'SMzwuqDl&rl+wg$du||)H){PN!7B@s$MstsUP5Qia#jj^aRWQdowW6imP`85A^!F}{0+V~D!*b!z|FH54HFz{pWP^0fm~k8=EW^F'
    '5K9pxlzJc0gC4}RpG8b#sx=ewl3+o4&Gm>{@fCVXLw%90Uct`75;Ql8PqLvwH~yL8PR785)&14$Hl~!4==j}8o;yDgiFfXu8!HwB'
    'HfZ7BP%V*TeI?h9Zh||fb5aKiFPuQStwn^a_mMl$sPEWPQ?|9XOm^C&GK*kHM0e&Pz_vQH*jc@cGR^DWh^u<Z-PCBIlsT$S+f}93'
    'G|U)kSdrUR<}Oepda$$HEL+rQei&*`Tuh9J)l5*Aq0H^a^w{SZD9In(jiS?T6Udk(N7T?y@$eK#8J@B^iox=xx)nSl5S|FvJT-Uj'
    't1oBa&P_32&8sCDG(R1pl$*e5uvL4JK{<A!{J5~aijhRcf~dn+jXbjZdAqMUn!~HWM@jN@o-9+$zC5>@N()CmV9iQm<o0EbmOaUO'
    'Nvc9L)_;c?x%7Zg&SEmJT5v^~EHJJ-W(cME`LAL!bEY7xWX6scMZ&zF4@x~XR2*Z8k!;>a5ApiCtTH9apvbx~&TO#Z#%X--joH44'
    'KRWwhHa(IOj}YhFMVfJFbf&BMClRYUfugs#_|)cxSsg<{qenjO`W&GbIYs?l>@cmJrxa{O!<`?k=j@Ve78_YA$uZ+|N<AiQ6f%b`'
    'j>aSt9CG{txN~+E^2Lo{r`j<U&N$*e;$O1XY|@(Qj3U*X0K+XFAq{wD!fu7J+=4_TEyUWSBaa=QRus3dg#8oapZ1BN7v6noXg7W8'
    'IW8Xv(;G?=K{K}R{%VO5mpxDaPsh`%II)~Bt<ka|oK!T;b@Zrx!r<hd1w_f0?=?VnEA``Bt>va&zc%WS?Gjl{a^oR4LyqxH{wWMZ'
    ';yay09a?DAXaU}gMpBH|3)FLs#91ty-^#JQ9R+CW=i6b6L2C!J-Es*P!%j=JlhJn=&S-nn@0iwA8cqYe7|$BFp!R`nqcjfM^}NFw'
    '^d8+K9sQVzWsG;AJPnxhDWrnw93EveW!^R1F2*qRhS7wh?jgQyV7P+KfyJH2B|O6dV>JmZVzHKd7ouy#ADzygN2}#Jg#0@UNYwaq'
    '4}i&P;TqFhZ&hb|TXSf{@+DhAf}>;cs**8%th-J9$ZHj&dXF~6C3iw?2gtH(*zHJI?I4tPEQI;UZm(Z6KIM_wrbfz1^Uo_8*1Y)*'
    'DRrfHpqGkdh*!5~q7@!P9Nu8Z7kI$EHa)~0;9+&CL=01QwmscrGP>|hw5y=AjYm2^>K}}oFIOK=yKRyJt)cdJxb<Xi!X01zy;)!('
    '?G>nY({_cT4$r{Aw)TsP7Nv@#inkziMuwKQaSi=A%5@6zwFQW-$y`VF_1kS|n-RdB1{DS5qo*Ec)Gk>JSF_5N?G#*G-@ja(E!g?$'
    'ZFpGafS6(!5!{X2M2y=Oy{S!jVVXk!9`r`0sC48GM4pNlz-@xg>)}hJyM@S)(!4ZE{2G!FXv?aIsL!P8ZH_zH5;y!V!a{9b64+jB'
    '%=YZ-GK4uwFX<lyG47n6j3rE}%wM|Ul_3Cz_liy&hL&YczC3R|P$a0UemiRBy23<c-3IZyWA8FnYb_VTsi5^=?eXs$VGp;wS2Wh!'
    '5dPnd+N8M+{X0M-XV3_3TBjSfi3}#5)UDg<o2{217-=j}Rm0V4tk3k->IDnkprDIHw>F2CF`MjW=-hFElJ7Ssp#6ldiN(9hv<Xr_'
    '03w+)b<pDR9uZ1xmz*4R-KJoWcd@k)gjHwsb`^6^N{#_1QoydVK4qQId9x^CGt=fu=Q|xVBm;K4&<0|>Wu&-q_RLp0;F=0&pm(cu'
    'Igtr;JILTpmgOR!nj4_n*~(TK0FOe0;f@E=vDM;kx69W|(^ffq`TC+}V)(Jl#!Z=yxy8VYoBwdiq?xYj*UN^iDjHK^RV$Lgm}_1X'
    '_dfn#%E@&$'
)
)).decode("utf-8"))

for _name, _source in _LIZS_MODULES.items():
    _lizs_load(_name, _source)

from scripts.v19_terminal import apply_overlay, terminal_market
from scripts.v22_market_impact import reorder_market
from v23.planner import build_sparse_planner, PlannerConfig
from v23.state_encoder import get as _lizs_get

_ACTIONS = json.loads(zlib.decompress(base64.b85decode('c-rk<%Whm*a{QHn*0W%}NXk2oR5L9MyD3m=7sd^u(SXM=V2l@S?+pLDr6yT*A8|4w^5iW_ZLL%)R@FW4lNlKq`P2Wr`nO+x{m0*bef3X&`03T3etdWP_UHFEA3pwgzkl`c$3MLK_h0_=U;pd#-#-86AHV$iAAkSv&;R@U(ZBut{{HUmk8eJ{`t+y6cl(>qFLs|k_tUHI-aUR@fA#t2Zhm<8{mt#?Uwd<R`1H>T{N=-U`~CY*FV?^P?NduXyc)cE_}@SNVbr1b@810N$M?f8u13B3>D6KX;p5{^{BU>w@w>;Dr#Gjsro-@Ie|tOZ|3>J|hyDKT@H<ztzkI*Hz5C(wch>VR9h*7q1@7mlPlK1UX~w;qJvvw(je$J1Yd8qAkCNxUzrA_0k0ud!^Y}IV>`8A(8=k*68g<mJ-`@UVuqh@3@jUD8&q{N#znQmZuvl+C?(gTzdiJiktHCn-aQEYU8KQmj=g(_;^4_%9Z2sZkO=e;?jDwE9xp`ja#}7VkvEi^J7QkRYQ45Y^H2S18y>OS~sl<D1z9q;LpXUh<>u|Kd9HY;fbNoC-Y<R~{0Q-9|&}d$pYkVahwQ!RKw+KJmCLPl!03UnWbRQe<4Y>E7HuZ3rpU*cmqsly+1AThj>DAP_7}yz!u^r4%!6TkO&KAo;k75g@v|GoY7(R8GCn&F8`~kDua1&VS!Z~kWeAQ2wpZ)%c@#1Zo8)W1Qz=Eo7)0?~7+x?r5KmU1u|MA`JyMLLUO69}c`9OQAbw2M5b9OXR22G52?8&K|eI;<aZKL@s++z0fn2*6W9C!t-kPPP<8x7jT!2BM1I$%TOojhon;XT*t>C=u$I3J`}<00VvmPQw1K(0woJjKRK<(J7Y;g`}c6Zgw7yt_e!s26?iY&7z^Bcbj}hPG(yCiXT<pbHi4lzz8?dAQyhbfE^njjU(ws6oJ4Y?W&*_J3Eh_Cw6|1>KczKl^e&Yg#qXoZON?MW@+=qa}t_MQ-Pki<;njEvrK?fYP@)w{(i&UilU)HG?pM9b9sKw>%354K9?DQG-vmAHu96_`v4EkuERYTIw*#;=!YKto9HVIDs&%4<^T$C>yWR+oQ4Gm${&35bW<CZvFOvZx85xfCp5DHd~Hd103?pfRQ2?oxA)|o`+F<^sCSR_Q0-^pgT7}^EO!mQMCIMGgFH20b;PUM((?t`+shCw+b*E_R)lD4BiJG$zu=u25>Y`1r#1Mb|~h4V(L_YTy%C$9e!*=%3*}|*J;c~L#bg@5d9jj-N9Nv4%r~s@6FEOr|}IqdiKo9Opq{+EGc&5!iVKq80Zmz4*AUh`u2dOA225muY9vhvKt>s+0&<8nFwHHT|OI-A3omS9R9SwzyI5B5$k-cl-$i=>@MQQtR4y=utbzG8$vypS4Pf~v?9mS0D1=V9L%f(72WU~39cTNw;M;+)flbJK!!AaTd}fEuTIv7_PaX5f3z9~JG#lLUm`eP;mpm3r*8qZ$He}_W4k*|U;Og1<#~btx^rVntC&$@|85=^J_7~!TR8P=h|*qWEw}SqVi6LwK$J%XEf_k&0kiy-7ehy*OZ#wlcl+CXH;vZk4?NG>r=$6;7z7_+C1!lOiyJsyU!R(Gf7ftY2rsCZ)iodX;64(DU^YqSwDe%7(2hgtnv0n!i^X@tl*GJ+Aj5tY)B?+ID`68Nl7s|R$|(H&WiLd%PlwfEqaorwc$r6TF%mpv86uOpY<sz*gO&<DR%eG%et(fE!7nr829G`zBAC%OdKi?@E1O#E=dkoHn`qpc${^$-!VQ?L6%*cSHe^eQAY)rDP8j6&;$X1>2HvTQnd7G+ACQRpcCon8EW!w;U}(4A=SC}sa-35OA|{#^MPjIXq$A?ob%jhem0HM{&<%A8wtuM1goXcz5dA5#+GrlKnRHk>VWJFz);4D{Wx}IIpp(j&v=Zuy>!~zbOAHv(iVkdtcDr0N1MYHo<ith|Y~u9KeToXi=uuwv`002og5LHGM!YuCBapRo<8?AVf3d^Ec)860fMU!NGyL>K1=h|mhSB((j{I4+ml}KT8-Rg;kV6~kY6#pz)&u$y<)969#^?9*EjpiXCD4a%T^VKfb<;iD*h+C@8Zf#oTc5R^wRA!mv-M7Y?<MMXQD{%c!zfD7^pcJr*Z2jB5TRjH6DoSk3OY8RMFvcgOfpb2JfsJ=#IvdK{kz-09+z#?^@N|65~O>>Ezf7h)00<g?HE`S5GOV3a8)MZ9O@#P^Bv~`!1W4`4o$Kx;p1nbo?34IdE^}7T`}N&kIYMiS|N_O@Ar0%_i64&CzM1kXTlsBT-g}!jRvbD#?w$jv}M<0rxrE4b#j*kYT#;tZX4OTP!kpXP8V$e(dMBuXuw^ekEl`c{b&X7Lx|h#y4qc66dY4H@7Y(KQX<5iKX-G<NgQRbbU{jT0~@1+_ZGZ`g_G=@YXMyl%_ho&p6F!PJ~JoThmZPTueb01;%Tlzeq#(o<uO8GO(y_{7>G-Ltt#uuMD3FB-aJv``eB&>`fCzE??fj=Fl8H<HSvefil#sdjDsmL?cWdQo8XEPfCg5b4zl#)Ex@&EBv-b~atC5?K3kNrPLLP0+=uZVv;>QL*CzrnWs`23s}Y)z(8b(G91==Kh`AGly}FHIBnfC4UHr4b>0u<(P_!65ri0*G*-SXfKsMxaC@*{fPe}4y4u)%JNG(T)(HV)(CW5K({>n>e$j}FZF`&5~Z~9s&N*4LO5wQgLXG3pG>&Z0QwR&*VH)ZSrnzpd((I<=KFw`}KEORwLkInWzhA=%+&ew_L(lPi!MV^$VBP9mq8+`VX@VV5`w9M|A+X?O2%ICk>c)mz8zn0-#j$BhK8@Ct-r%$=W$lx}yole+8W7mBtl$V(6mZiM(YN}e8Qkwe0%-)O^U2|bxJ(QGx(7NbM%c8t=xRkn8t-BohJhvQ@?Bz_D1~&lzRFM=;gE7THk1+cv@C^GRi}7Rid}<-hzb^?Fp&fAeM$gl^4+1RHj6vAP40}3ha)arjmMtE&KE)bq=p5?!1!G^ti@d3uVJ7atRtQUmwHf_{HW{mj+5m8?Q4K}WKrWL-_^w8BbK_oJKbSWc$<LtcAH9dBSeuk<sH7Ky?5mY)NRb^uNJ?-LX+ro+PH*K+A^~$VtQDY!HmHl9U8IwraHe_nU}wuX4Q~vWXx1Q_LrJgK;o{zDi<<-^X5(}ztcn9U!eExid`K?s5!v;`GT<GUnfm71Dp>!k8dnuM*o|fjmL%kb?(Ger>Au61UNUzF-M$RECA+k(RG`&^nM>8$lZb*$&NK8a7Rj>~Y)OX`@N*Z8kDI-&V?yD>Y?RLuON%@TkQIxGtb3EvICA%erl_Grc!$ICBJ`?3{!|q^MbiY4X;-fL7laBV5RU*$j-Cl9IF>*?9O6_-BA)x>W7(`Z_hPaoy0R<@k<o}g3qvxy;Jawr6ulzgCes=8<bOq5<N6^FCJIn71Sw+b15L%LU{m3&3sqJ`XY;ffrh=tITo1@slryZ@_5p@pV%?dL5O5|MDoSTtSY1>TI7OKiM*)`wmmEsGB`eNXDyMFhkbYC9O*ja|T4_TmX)m&4`xa&F0MospHkWWWV~ytEZZh1$IFB4%Uko0HxNJBi>5EzDACoy1Rx0ce!?MKsZk?H$3`K^mP?sY5oUM%;uP@_#rqZ<d1NDn+ErQ-mH8=bNyZ6|e<%^ERy&<R4K=pg{m)Y>Mppm4F)c#K8y}F#llZ^E_;r+`(z-|c5ohLOhhSW~)kGgy<;BaRJ*&y7O5+B)js|cQMQ=Fq{QsW$)EJ0D?d5C$=TO6qaLHaHcz+9qgMY#+&AJ6pv;4;c;oN<gYudPZLVnk@iLxhb3dKYWw<w=tabtBnDvp4$$Yb;(Tb=rzci9m0|O7s*-o6?F{yPDEEsK<t|K-~j5;Y`d}&TG$4G4^@+{<g9=TX09>v?4ezU6C|D-(V(MQEYM!Fo{C+XX54-#NUY9#;6mTL|-L7!u&Q=z+1o|SfNdwg-cvi#jTbRf6>*>9=^CxDMQ<gcMZ?FVu!N+^g;r`W?E<pT#!bm4=>w;zLjx?rB8}@ViHy?cg~<gO_6EWW&##cl%BLWuG$PG*n;iXjgY(q4+)_mjWi8iWFtU&(pbsBH$VL~&s}lM&ODqir<@78s}QQK$&!N0;dESZP@zN1CrKS5C&#LGq2Xzu?;etFXaG!HyO}<^pqWB%6a2PR4wkPnEj%BK3@i0AGg?21JRS6Bj(2$}m1%|S#*!wSrChRJfsV9Zw~4-7ehs)w&*ub}DhsiEW9D*2A1#`6D$-8eMmgCapAmwgBQ|0ROQ@zSueeK%>n_S4l}HBaT>+Imj-Jn`30jCZ$Vd`(^`)+Cd{z#@<YHYcnIks+av3ioR>EQ%w%xl*ddgw%=!oUi$SQ`li{F4amf3b9w4z8!jHOZu`EZM5fT^#BZ2NZiXohu=e`#g9^)XOhe+|$J&-cP7#sZMaU=Luq*a#(ZgKx5bi$d=WX#~pWsKP`#Qm*<43+hys2sIsg#xg-FA`Woh$f<ROt-^K!EJsevNBrk9f~h@tMOS}j4)HMqWqg2NJk8b9d!3bY5%a^s6yih4EcYWP9Fcrco$XUEb{5kq>gO#dh+Hu<26DnGHRXM0I5&;^Nz6K6Lt&IVbaM6ruQJ8yYOK$ehb<SS?89k^lOl&e@+#|us39_P2soVe=b3A~ZyY3X^V~e+n0sTcl+21I!@vNgI58)HNBRuZkpVxN9-1?m%C}PyimWJGKjCEqRgSK|B|G%Fm{NBTO3@q1$GeUDrNwe0i^cin+QXXD<K#ueuY?JaE_}DBVThEI@PAioO5+;NX~JaLk!TC4t8iNS`$=TVo4cX&qh>Z}g}{46X89yomBxl^r)AVg5l}I$TU2nxB4%izlVEa-<SYBx((=8sIo`@SDZ800;Uey=)WhosH%o*CorzyAxdZb4o5DC|egQA)rz@(cIWu|K4D~M|lkD5g`jBYzw0_9vt@!kY$U!&maXrac&uJkWsL?uG(jmQjVqyiSW$RK2T*t?decot25%sf`zqhWV@T6O+GkVSoKlB(sr$CH5kCf;cb-cDiCh<Xu4PVO@W^*dju@R?8GWX1$SYOWA{W2~|a-bM3!RciJQ)C#m2&;wnQ_o?~#KXJAnXD?MYUU$NM(keDyY6hVx9|S)*qGxBLO@}uLdV}})0xiJ<C4<v>ua7=G!iDp4S)R=@m)IdifXAZy{=a+=Y>NZ4i#l-CX7{DtAe+lW5Eb5szChGD*;JQ7Rpi=ab_T3qXY<DQ4XElVsS{Y1;WgQG{1%LL^{#|8zq18JQqiK8W#}u0-S381bo(H#i^#$(sH*MEoE0#Cx?=2)honbP}d$QG9UY{ye6Ejk*LBpOz1jxE-RQJ#LCYF@QV2uXcQWD6wB$T;mYf>D5`QQi!}5RD0JqDE;*#LsA{A^<U&t+qL8#qVYBFT?L{H=h`3TYj<JY)3W${isMGV#7?+ijvFFMi2|VmCCwBzqW_&@+9?0#ts6FuoTFB#JF=wl+N)1aX@02$#T<>iff==h!Ap%cpDETKO)T0%Cs!#}#aJ+5t(&WZHyeJ&Lj1kzqijq`z4{2aQ@Icy5AMa~piO-CF7Sq~zF)e)dBeoBtx5)WNvU{9ouU$W+0g*||EO(V^6Xd40w<<78!BA`Q7&X7rT}ddF?B#ORy40+;*Ub2FLgK`ztA@WtGF(cR9CQq53!7{+0$b_P{%2h)zYuk4x}(A0a)Pk<XT|#C1vTUeK&7CgjIe_?``{;fw&|5AWzIB4as{X?s;oZC$tv3p&qWqQ#x+t@ctM!$Ledf=@6cduu)f*G^{Eggv=8cd5iq>P<$0w2k1&f%$(x37$7SLSx65B0)N$B5$5}Yk+H`M=CRJu_#l3DbptSB>`cot4GWz}MXRk6NqFYP{3i=>TBlI35Ge!5(0!L6M4!Yh3+ke#tNx%4n$n}?7{VA^6Xvnx~;BRT}ql?CQya!e%zAFLJ&=C@h%7!~!Ps>`WcGSVBjJ1e@kXla)Z5NCF<EYujJuNCX#WjeS2dhB+Y%?uVZ3@3^LzC(AAtz@2`XOJiinwL1u{Wp6FckcJMT7XovCKj<Z<8-|)ykda-h(t@qyN|*^E#iTNUL?p37TWcFReCJ8`?3m6^&&y*2M)a)pnS=0+ry-m1BwL(rfVmVaqQD=#BJRDXvvl?28^Ntt>%j6-1OvHV|76vSopKT6Z~SAK@=aia%bYsCR}LYQ>T-Sr%Wz#_maHQ-M7MnvkHE9$Q(ca8m_Zg03f)XxLp{Yq_4=3^&$6kbw4r6RUNP1=9&N)5rqv7xe1v>JpXrzQk=x3bMh3N@o;sl;KGmmi>Bs387!?TnbqXbljA!S>El-$+;X{jc2Xpmf(qU5mlmD(13e4%fX-mq16F-8hC&MJUPe>u~ijx!bCP4US67xwsr$OuB3Yx9hDD3z{Kd`m%MhDIfqm|gpTkpWNsrHgg|6&ePP>01bEfNyU-zk{dh(sdLmbC?7PtwlSkMMyxsL_)rweYxrHvbYBVH|gJ^FEZyOjqRT+a6#Uz87UafjKIU*C=VP#R%)9U)A8+v6pgE5QVkkNHbI~FfiRxr@nqU@)Peq6a30r;3yGKqB0UDi?5D300{BPTw$Z<{s*$fnF(eb*g1@CTI{?iBD#lKHQ+T||>=W4X9UcB;Kd`ws-@FtRi|J&j!|JDNk91xJ3#1o?Op<J-A7L5P5?88NscE-4pqJ#VN$%{TE#k@|vPpr7&KNY<)ABZWe6P&0b(IgsYXCLf-#h+|mTQ6*a9vWsU31BLSRtYWKPHd5()Z}&Fk+|kWNn;#mf!0&#?#Tl1Ut!vrBUd=|y4zA;ma<E5%A3cxUEulg1QAT*GNHFjGNh1D{rzu<VP@ZFKu_Bj~--8~^#LM!Nmjzlhb!~KjUk~{z;H!~lBT+rm1qfmEh>+ge{;|v!>r!NctWgU4@pL$$^{P4>fdL5+-p)4F8S**~J~0~1Wuy9b&gN&3hUea2=7TkE1~_Rh*T2tpD8~JmibA7JEGe4s>m1Mbq6g?B+WP8RYwdX_fHLJJm-)FYv_qjin)sVMFjP{xp?aZYr!r6*9---6Rp<pdM=&EcHP89r?9j-^y8wmQ`M9T0;Kr!DK-h6|zD5!tgek~e#Q?u--(e;I)hFH3O*RhkKr&%RKHF1Rcxx|%C}>uUg3mkP0maH?(<r|INPpK7WnI@BxbD!5N$aboc&n;1Qh&zxh0{YroRv_pgOmb9yAR;bv@umf-4u#woLDez;?VzhT(Yd9FVnqmpqATnD1nZ##W?fM00Qev_iCy3minhznysLOFP3&G(fl;)5!2sHD4inLys^Gg>IWj4YKac$$;71S0CEBMyjFuHzP3+tSypZd-p2iCVBx%;fw5rI>BS@yvwa#s(L}I~6q^C#P?naU;yCS0Ra%l9FB<!jzvM=~`u&KVn~>aI3J}8JksLWYndIa?E{FBv(voo|{vn}tN`yhFif3y6ABSrLhr~|Try{R}DrPO6^tqQHzx(yD4~DuAJQ`fV!dh720<RLYJ`P<Ej$()aTNQ|JuH0on&?X|g+S>Ev-iT{l_w@hDt~oQxtZ#}-PL^{_%A*CAGbM&QWh<{b%C>6N?WAx<H@m*oyE5HUm6u6*stkHxVy%<iEYpSkSJCD<`@)WQe1!D+N~_AYNJ-QBQ1QmDpsp&N0)n-00OWS~E>W3DpCA_U6J?9j84R_Gr3eWA-Pb{0kXt&|U((p6LGu1fl1qikIVQ&Xay-*)z2&cnOuAU1qn9O?LQB65k1~uw#!*0M%W#TPtWu|D15bd-_Oyat>Jgqvrd75Q(}JASBtU6VW}BJoC8X57I^>M(l#MZLiV3OgO=Uh(9LHTX4Ydh@wMfmJ0qt_-wk1qd%5jr4DtXNs1Ma)F`KT$)w`7^_WEGvuIy$OQ;D@PFdhEIqF@a8%S&FtDG}zTIvez#$plhiz{%TPFP%TL9$gv27qLsQ^Da<}q#RX(WmjS3%!#*45Qzkv0fS9-gBzh&^y9FT$i*660JF1Gz+y?ZW<48hN_W0MLI3*p6wNLui)pyxyk7R~F9l7^+MFpC!1C~S2pzs?R?Hi_Jta6QO`~EcECh-?aqQZkeuEYxy^dn|;n9xszVLRdO-BN_woldA-ef6waI0T!DZj}*gDJPYo^GnlbnI;~CG6kf$4`5xIO-ob843GS^UB&K&S+*4_2u0WzB{d2#vs}(AuTu891E7#$Q<EVbS6=8zaa)^AO?(}wWL>9j86_=|;ViB!Vt^Zsh2G5bvUtm5a~aq^YrRPLCNLYA<ESw?(b<qA_Bv#*%o%_|12D2(T5<}>*GochYq=Q!nM(KVQ#Fo>y#}A#3v88?j0Z%{wF?Y#f_Kh>Gb;|(5jn*$Qq1R7)V}d7H}m3a$KW-Z{9Rw#2b+Dk5Sa2wbW6xGn&#0b7ikhG`cb5c|IoBRP#-`hEo{_J&Ome|HUnBv96U0-?Db+SUM5Du3Y+WP)?ClGiJm)Y@FK(4sl3Oe{h7Zk1aZ%_IEW30V_*nC4foOzH&!)T>#5#(CNSrO#!$LbFxOxOuM2k00AiLbYPz=d$dbv(U5qo{SrpLN_hRuhjgVYWY3*uhPV%%S543K-CfwZEolk6r7iKZbL@|cXzL*5A1znXC4+9o97pVxO<vV3?xfW&uMUGuWFW-M}q`G?eY@T`z*PyYw6b=p315E(=dZj2{msF*6k!HrY8iE!4x=EzyAtPS6C;+Y-q~GH*kvp+)i906H{RxO`q-B|j;)HjtDJU+vY?<;kD_Y~IAW7>q)*v92b5tc!gQ2SpZM+KT8D)?fBg8@ErgtU-!@#~l9C8XH8V)gnz2V6)>Wd}EPG?N0RhA0+`|7TE4=ceR<Cd+DX}6oz2x-QAM?7~TV9_H|yRj!s?g+6F)IvM+U+gU+lM&q1wUM0~nh|hSQ`%}{7w%G0{bV94Q{zllKXUs-$i^{^WEvNd*~@CBKVzNJqev3c*TXK?2FpN0R(yptYk*3aqdpS(<=|k08TC^3@pN6ZIkab@m5!EiN~o2EEnbF9DnV()!tCOYI<;|9UrcC`A~xtG{I)0|RL-L=B6>F4XK+3_$;*j7oH&1JZYKf4NTRu3gG+>jeQKt=YT#kzl<r9fhc0^*6UkWx|J*ou9VH8=e;X3_E1_2M#(Ri(B&FY;dbJ)5)`K^pU#YCFlyV&23>|#QHSFkRH1n_BW$&zCE|w@(-YE|H#*qkF^E7s7m@UKZ6h7U%l8vq|`XDXTN;vd(vX*QOxRR@0o&#F)q!>!GR;!qJnp0Za_`4nn|2)ka-V<m_;VFndh;!ISevu)C`t-eM@fUzwaaKAh4Hc*1%EyK;!H0+8X~d$$i>-NRFzgQ<7J8k&m~iJ*ztfKo5eQ5Gz2x8|!vfJj3_Lvn4;K4;ojN?aX^1UkmzSCvjVQ_4kDUl38+fr}M%5@yK&vF}f1g1juWaL!SR)AqfK|sRszGA%XUat>IhQV$7y_0D=P3E*f`!}C6Q>Z)R;;S=1~{(PufKrU)K<ulIs23Kh(f?Pa?pC8mm6D&PY^|I)3hP<O3@a8G+0uB&}4s*R~`DZ4n;Q2D$5g5)2!TX-fkBQ$s(oll0Ht^E?EdqlSG3Hgwh7A0xePPDlM<S@0e3+a^~kw=hQke_q8g!AFoqNKg6)Q6MFKO=FUV&<D*l_5LOb3#Z1HwA&RwICCX&OIaLZ0#`A8ex=&68FFksdBkpW_a)k-;d&pIam3_5Q>IlDG_c}YyjfF|B`%n^C4$}k$NpvWLCL1!+aKn$wHl61KkyweCaqj@^;`w*wt4j)6!Wk$5Y0wVgDu=yz(VyJem{Yx!nRxpaiAZkz4Bs*p+FaUvVmXjR1vfo7iXO@|2%@&ZHN`03o-u_>Qh!^EVe8jiqSM7l>P(m_Iw=w&6G8w;PnZrjiZQ7aevC)6K!CPiP63L`(&gTk=4Ojw(T%WL3QC21SRB7yZ!o~R`P~4l<A~j+y-&}sK&$3V)-Z)t_)!sFWyy&GB-TI*bW8w^x2r<S$-`m_)f5aO&|<?9gnHSBeZItfcTF<6h`3DoBM@XuUY3GzX>wd%IhRRowiN^kf(`@)Qd9<-DJ#;fT|y&*eK>JBtFbF2%bOhSI0*SPt=Dy#zdW_Uu<eX&2NP^Z2%n6$GeebSERK3JW%$s2dC?*5386ZvV3mc_c9e#RXKn4$FO57>i&>mNoGs&7ucXLQfz^XEgHv9)8cYopm>55%BabA#6HSkEh@enWj0H2D+*!54M5FaeSe_KGdk$y{)>jgBxM>v#I;BJbPAK}LhFXFQ)-(jds+HlHbr8T1S1mol9O#cx#0jh%9qsu(t?inlYI+AK3*R`*qWdYa+2YkF=r$#wYRt=uNXUnbz-L8Ng9h0Wn!iNH#xD()maRqP-$Rf1VabXt)zFLpvXF5+^n(`B8bDKXHmQL!D&{&bx+ysvM(w8_aLS=2!reeD@fhL}al(x&>0ToKnI}J*QxmTn9d)%tO$q4GB{D$ka~t|?l!d16PhEXTL5c-{it{YoV$^Nn-N@n>%zsTcBhG0SRw_9T4>31e8$z@;8MwhjJ`w4O=0bHzq<EEM1a(JkhDj|5n%81zU1DLcMEfLEMA*A}X`%#4n`AtCDmUVPY*u!{5ugZ*9$)mmaGj3TQI9e%>!+pCYRf@)Jb1Evv=Mn7A@}Y)nEQ|HM7zc6h7;6QiITE(?4}#tA``aK8~EK1xizO()4I(GdE^0<0UjV7!sv^$KUZbOkmo8*r=L!@SUJAFyjIVb1;szEc!lf{OaY^{TTF8*5eej6ZF*-%B{A|;D+WbrToySm5Vk=%+FOTXyY^KM!r-d6M#&+i9po<Lfl`4ZuSu#i<4n+YrinL_SuR;!hF-X*b0p1B<IK}V2*w9zzMKF$hJ}d=zLwd+<jN&x!&2kmm@ZSn&Z<!eFUP)NIPA4yKw6|zOAXm^8E{E`YW(~>x`3Xl7DcWagIJI|F4kBv1~72Sh22GyLmLBj5UV9CUv3mkx^CGhMC~SRczb{Me%gfR_lB?ND8P?CzR5I7<XY;c`XSobsBfoNr*BN(v*aD2Ga>YA^*M*>;r{@R#*Y9')))

_PLANNER = build_sparse_planner(_ACTIONS, PlannerConfig())
CLEARANCE_STEP = 630


def agent(obs, configuration=None):
    try:
        # Step normalization: Seat 1 in Kaggle Environments lacks 'step' attribute
        if obs.get("step") is None:
            obs = dict(obs)
            day = int(obs.get("day", 0) or 0)
            hour = int(obs.get("hour", 0) or 0)
            obs["step"] = day * 24 + hour

        step = obs["step"]

        # Base planner with closed-loop weed repair
        action = _PLANNER(obs, configuration)
        
        # Market impact slot ordering (safe sorting of sell slots without order dropping)
        action = reorder_market(obs, action, mode="impact_slots")

        # Step 630 Early Continuous Shed Clearance
        if step >= CLEARANCE_STEP:
            action = terminal_market(obs, action, "collision", replace=False)

        # Late-collision terminal overlay
        return apply_overlay(obs, action, "late_collision")
    except Exception:
        seat = 1 if int(_lizs_get(obs, "player", 0) or 0) == 1 else 0
        farms = list(_lizs_get(obs, "farms", []) or [])
        farm = farms[seat] if seat < len(farms) else {}
        return {
            "farmer": ["PASS"],
            "hands": [["PASS"] for _ in (_lizs_get(farm, "hands", []) or [])],
            "market": [],
        }


def _kaggle_submission_entrypoint(obs, configuration=None):
    return agent(obs, configuration)


def _kaggle_submission_entrypoint(obs, configuration=None):
    return agent(obs, configuration)
