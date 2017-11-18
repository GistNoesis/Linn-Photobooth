
typedef struct  {
  int ENABLE_PIN;
  long lowerBound;
  long upperBound;
  bool speedMode;
} StepperExtras;


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

#include <AccelStepper.h>


AccelStepper XAxis2( AccelStepper::MotorInterfaceType::DRIVER,X_STEP_PIN,X_DIR_PIN );
AccelStepper YAxis2( AccelStepper::MotorInterfaceType::DRIVER,Y_STEP_PIN,Y_DIR_PIN );

StepperExtras XAxis = {X_ENABLE_PIN,-1700,1700,true};
StepperExtras YAxis = {Y_ENABLE_PIN,-3700,3700,true};

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

  XAxis2.setAcceleration(1000.0);
  YAxis2.setAcceleration(1000.0);
  
  XAxis2.setMaxSpeed(20000);
  YAxis2.setMaxSpeed(20000);
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









void pollWithEndStop( AccelStepper& stepper,StepperExtras& extra)
{
  if( stepper.currentPosition() >= extra.upperBound && stepper.speed() > 0.0 )
  {
    stepper.setSpeed( 0.0 );
    extra.speedMode=true;
  }
  if( stepper.currentPosition() <= extra.lowerBound && stepper.speed() < 0.0 )
  {
    stepper.setSpeed( 0.0 );
    extra.speedMode=true;
  }

  if( extra.speedMode )
  {
    stepper.runSpeed();
  }
  else
  {
    stepper.run();
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
      StepperExtras *axis = NULL;
      AccelStepper * stepper = NULL;
      if( intBuffer[0] == 'x' )
      {
        axis=&XAxis;
        stepper= &XAxis2;
      }
      else if( intBuffer[0] == 'y' )
      {
        axis=&YAxis;
        stepper=&YAxis2;
      }
      if( axis !=NULL)
      {
        
        if( intBuffer[1] =='s')
        {
          float f = atof(&(intBuffer[2]) );
          stepper->setSpeed((float)f);
          axis->speedMode=true;
          Serial.println(f);
        }
        else if( intBuffer[1] =='a')
        {
          int i = atoi(&(intBuffer[2]) );
          stepper->moveTo(i);
          axis->speedMode=false;
          Serial.println(i);
        }
        else if( intBuffer[1] =='r')
        {
          int i = atoi(&(intBuffer[2]) );
          stepper->move(i);
          axis->speedMode=false;
          Serial.println(i);
        }
        else if( intBuffer[1] =='l')
        {
          int i = atoi(&(intBuffer[2]) );
          axis->lowerBound = i;
          Serial.println(i);
        }
        else if( intBuffer[1] =='u')
        {
          int i = atoi(&(intBuffer[2]) );
          axis->upperBound = i;
          Serial.println(i);
        }
        else if( intBuffer[1] =='h')
        {
           stepper->setCurrentPosition(0);
        }
        
      }
    }
    curl=0;
    stringready=false;
  }

  
}

void loop() { 
  ProcessSerial();
  pollWithEndStop(XAxis2, XAxis );
  pollWithEndStop(YAxis2, YAxis );
  

}
