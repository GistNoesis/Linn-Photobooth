
typedef struct  {
  int ENABLE_PIN;
  int STEP_PIN;
  int DIR_PIN;
  
  unsigned long prevtime;
  unsigned long lastpulsetime;
  unsigned long nextpulsetime;
  unsigned long halfpulse;
  int dir;
  bool hasPulsed;
  long pos ;
  long lowerBound;
  long upperBound;
} StepperControl;


// Pins for the RAMPS board
const int X_STEP_PIN         = 54;
const int X_DIR_PIN          = 55;
const int X_ENABLE_PIN       = 38;  // Active LOW

const int Y_STEP_PIN         = 60;
const int Y_DIR_PIN          = 61;
const int Y_ENABLE_PIN       = 56;  // Active LOW

const int Z_STEP_PIN         = 46;
const int Z_DIR_PIN          = 48;
const int Z_ENABLE_PIN       = 62;  // Active LOW


void setup() {
   Serial.begin(115200);   
  // put your setup code here, to run once:
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(X_STEP_PIN, OUTPUT);
  pinMode(X_DIR_PIN, OUTPUT);
  pinMode(X_ENABLE_PIN, OUTPUT);

  pinMode(Y_STEP_PIN, OUTPUT);
  pinMode(Y_DIR_PIN, OUTPUT);
  pinMode(Y_ENABLE_PIN, OUTPUT);

  
  digitalWrite( X_STEP_PIN, 0 );
  digitalWrite( Y_STEP_PIN, 0 );

  digitalWrite( X_ENABLE_PIN, 0 );
  digitalWrite( Y_ENABLE_PIN, 0 );

  digitalWrite( X_DIR_PIN, 1);
  digitalWrite( Y_DIR_PIN, 0 );


}


typedef struct {
  byte pin : 6;
  byte mode : 1;
  byte state : 1;
} DigitalPin;

void set(DigitalPin& pin,boolean mode=INPUT,boolean state=false)
{
 pin.mode = mode;
 pin.state = state;
 pinMode( pin.pin, pin.mode);
 digitalWrite( pin.pin, pin.state);
}



unsigned long time =0;


StepperControl XAxis = {X_ENABLE_PIN,X_STEP_PIN,X_DIR_PIN, 0,0,0,0, 1,false,0 , -1700,1700};
StepperControl YAxis = {Y_ENABLE_PIN,Y_STEP_PIN,Y_DIR_PIN, 0,0,0,0, 1,false,0, -1700,1700};

void handleOverflow( StepperControl& axis)
{
  //We handle not perfectly the case when time overflows every 70 minutes
  
  if(time < axis.prevtime )
  {
    axis.lastpulsetime = 0;
    axis.nextpulsetime = 0;
    axis.prevtime=0;
  }
}



void pulseAtHalfpulseSpeed( StepperControl & axis)
{
  axis.prevtime =time;
  time = micros();
  handleOverflow( axis );
  bool endStop = false;
  if( (axis.dir > 0 && axis.pos >= axis.upperBound) || ((axis.dir < 0 && axis.pos <= axis.lowerBound))  )
  {
      endStop = true;
  }
  
  if( endStop == false && axis.halfpulse !=0 && axis.nextpulsetime < time && axis.hasPulsed == false )
  {
    digitalWrite( axis.STEP_PIN, 1 );
    axis.hasPulsed = true;
    axis.pos=axis.pos+axis.dir;
    axis.lastpulsetime = time;
    //Serial.println( "pos");
    //Serial.println(axis.pos);
  }
  else if( time > axis.lastpulsetime + axis.halfpulse )
  {
    digitalWrite( axis.STEP_PIN, 0 );
    axis.nextpulsetime = axis.lastpulsetime + 2*axis.halfpulse;
    axis.hasPulsed=false;
  }
  
  
}


char intBuffer[15];
String intData = "";
int delimiter = (int) '\n';

unsigned char curl = 0;
bool stringready = false;
void ProcessSerial()
{
  if( Serial.available() )
  {
    int ch = Serial.read();
    if( ch == -1 )
    {
      //Handle error
    }
    else if( ch == delimiter )
    {
      stringready = true;
    }
    else
    {
      intBuffer[curl] = (char)ch;
      curl = curl+1;
      if( curl > 13 )
        curl = 0;
    }
  }

  if( stringready )
  {
    intBuffer[curl]=0;
    if( curl > 2 )
    { 
      StepperControl *axis = NULL;
      if( intBuffer[0] == 'x' )
      {
        axis=&XAxis;
      }
      else if( intBuffer[0] == 'y' )
      {
        axis=&YAxis;
      }
      if( axis !=NULL)
      {
        int i = atoi(&(intBuffer[2]) );
        if( intBuffer[1] =='s')
        {
          axis->halfpulse = abs( i );
          if( i > 0 )
          {
            axis->dir=1;
            digitalWrite( axis->DIR_PIN, 1);
          }
          else
          {
            axis->dir=-1;
            digitalWrite( axis->DIR_PIN, 0);
          }
        }
        else if( intBuffer[1] =='l')
        {
          axis->lowerBound = i;
        }
        else if( intBuffer[1] =='u')
        {
          axis->upperBound = i;
        }
        else if( intBuffer[1] =='h')
        {
          axis->pos = i;
        }
        
        Serial.println(i);
        
      }
    }
    curl=0;
    stringready=false;
  }

  
}

void loop() {
  // put your main code here, to run repeatedly:
  //digitalWrite(LED_BUILTIN, HIGH);   // turn the LED on (HIGH is the voltage level)
  //delay(3000);                       // wait for a second
  //digitalWrite(LED_BUILTIN, LOW);    // turn the LED off by making the voltage LOW
  //delay(3000);    
  ProcessSerial();
  pulseAtHalfpulseSpeed(XAxis);
  pulseAtHalfpulseSpeed(YAxis);
  /*
  delayMicroseconds(100);
  digitalWrite( X_STEP_PIN, 1 );
  digitalWrite( Y_STEP_PIN, 1 );
  delayMicroseconds(100);
  digitalWrite( X_STEP_PIN, 0 );
  digitalWrite( Y_STEP_PIN, 0 );
  */
}
