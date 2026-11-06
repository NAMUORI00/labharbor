param([Parameter(Mandatory=$true)][string]$Server)
ssh -N -L 127.0.0.1:18600:127.0.0.1:18600 $Server
