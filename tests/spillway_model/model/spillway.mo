model Spillway
    output Real V;
    Real H;
    Real QSpill;
    Real QOut;
    input Real QSluice;
    input Real QGeneration;
    input Real QIn;
equation
    // H = h_from_v(V);  // uses a lookup table
    // QSpill = qspill_from_h(H);  // uses a lookup table
    QOut = QSpill + QSluice + QGeneration;
    der(V) = (QIn - QOut) / 3600;
end Spillway;
