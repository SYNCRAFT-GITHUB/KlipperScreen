#include <stdio.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>
#include <ctype.h>
#include <stdlib.h>

struct soffset{														//Offset is saved in this struct
	float val;														//Value of the Offset
	bool change;													//Offset set?
};
typedef struct soffset soffset;

struct soffsets{													//Offsets for x and y
	struct soffset x;
	struct soffset y;
};
typedef struct soffsets soffsets;

struct sline{														//Line struct
	char read[256];													//original line
	char write[256];												//line to write
	char dummy[256];												//dummy line to add .gcode	
	int G,F;														//G0 or G1, F-Value
	float X,Y,Z,E;													//original X,Y,Z,E Values
	float nX,nY;													//new X and Y Values
	bool seenF, seenX, seenY, seenZ, seenE;							//Values occure in active line
	bool isErrorPossible;											//First char is no number. Error possible
	bool isG91Active;												//Relativ positioning is active - make no changes and alert
	bool readOK;													//new line read OK
	bool blX, blY, blXchange, blYchange;							//backlash applied, changed
	bool G90;														//G90 in this line. need in start gcode to start compensation
};
typedef struct sline sline;

struct scoord{														//current coords of the nozzle
	float x;
	float y;
	bool blX;														//Backlash active?
	bool blY;
};
typedef struct scoord scoord;

void getFiles(FILE** fileread, FILE** filewrite, soffsets offset, char *filename);	//opens/generates the .gcode files
	
soffsets getOffsets(float xoffset, float yoffset);												//gets the desired Offsets

soffset getOffset(char coord, float val);										//gets a single Offset

sline getNewLine(FILE** fileread, bool G91);						//reads and analyses a new line

int getiValue(char read[256], int pos);								//gets the int Value (F)

float getValue(char read[256], int pos);							//gets the float Values (X/Y/Z/E)

sline generateLine(sline oldline);									//generates the new line to save

sline addbacklash(sline line, soffsets offset, scoord coord);		//adds the backlash comp to the new coords

sline applyTravel(sline line, soffsets offset, scoord coord);		//applyes a travelmove if backlash is applied/removed

sline plainLine();													//generates a new plain line with known values (0/false)


int main(int argc, char **argv){
	if (argc != 4) {
		printf("Must have 3 arguments.\n");
		return 1;
	}
	char *filename = argv[1];
	float xOffset = atof(argv[2]);
	float yOffset = atof(argv[3]);
	
	//File Pointers
	FILE *fileread;											//Pointer for original File
	FILE *filewrite;										//pointer for new file
	
	//Startup condition
	bool seenG90 = false;									//until G90 comes up - no altering of the gcode
	
	//Backlash Values
	soffsets offset;										//Offsets are saved here
	
	//current Position
	scoord coord;											//current coords of the nozzle
	coord.x = 0.0;
	coord.y = 0.0;
	coord.blX = false;
	coord.blY = false;
	
	//Lines
	sline line;												//active line
	sline blChange;											//dummy line for empty travel moves
	int linecount = 0;										//how far are we in the file
	
	
	printf("* This program is free software. It comes without any warranty *\n");
	printf("* You can download it for free @ thingiverse.com/thing:3060573 *\n\n");
	
	printf("Antibacklash can help you to compensate Backlash issues if there is no way to resolve it on the Hardware\n(e.g. tighten Belts, Pulleys, Steppermount etc.)\nAntibacklash is meant to be used for cartesian FDM Printers.\nOnly use it with Absolute Positioning (G90 must be in start gcode)\n\n");
	
	printf("USE AT YOUR OWN RISK!\n\nAlways check the generated .gcode for errors befor starting a print and don't leave the printer unattended.\n\n");
	
	printf("Only continue to use Antibacklash if you know what you are doing!\n***************************************************************\n");
	
	offset = getOffsets(xOffset, yOffset);									//get the offsets

	getFiles(&fileread,&filewrite,offset, filename);					//get the filename, open and create new file
	
	printf("***************************************************************\n");
		
	if (offset.x.change || offset.y.change){				//at least one backlash needs to be compensated
		
		line = getNewLine(&fileread, false);				//read and analyse first line to start
	
		while(line.readOK){
			linecount++;
			printf("\rConverting Line %d", linecount);	
			if (line.G90 && !seenG90){						//make sure gcode is in Absolute Positioning
				seenG90 = true;
				printf("\rG90 found in Line %d. Backlash compensation starts from here...                                \n\n", linecount);
			}
			if (!seenG90){										//G90 not found yet. c/p an keep on searching
				printf(" - looking for G90...");			
				fprintf(filewrite, line.read);
			}			
			else{			
				if (line.isG91Active){							//relativ Movement active, c/p and alert
					printf("\rWARNING: Relative Movement detected in Line %d. Check gcode! No Changes were made\n %s\n", linecount, line.read);
					fprintf(filewrite, line.read);	
				}
				else if (!line.seenX && !line.seenY){			//No Movement in x/y, c/p
					fprintf(filewrite, line.read);
				}
				else {											//absolute x/y movement. adjust line
					line = addbacklash(line,offset,coord);		//add the backlash compensation
					if ((line.blXchange || line.blYchange) && line.seenE){		//blacklash direction changed and extruding -> insert extra travel move
						blChange = applyTravel(line, offset, coord);
						fprintf(filewrite, blChange.write);						
					}
					line = generateLine(line);					//generate new line
					fprintf(filewrite, line.write);				
					coord.x = line.nX;							//update current nozzle coords and backlash stats
					coord.y = line.nY;
					coord.blX = line.blX;
					coord.blY = line.blY;
					
				if (line.isErrorPossible)						//possible Error seen (char after command was no digit)
					printf("\rWARNING: Error detected in line %d. Check gcode!\n Old Line: %s\n New Line: %s\n\n", linecount, line.read, line.write);	
				}
			}
			line = getNewLine(&fileread, line.isG91Active);	//read and analyse next line
		} 
		
		if (!seenG90)
		printf("\n\nG90 not found. Please make sure you operate with Absolute Positioning (G90 must be in start gcode)\n\nPress any key to exit...");
		else	
		printf("\n\nConversion finished. Please validate the file and its Start-/End-Codes.\nTo preview you can use any gcode viewer (e.g. gcode.ws). \n\nUse at your own risk! Never leave your printer unattended.\n\nPress any key to exit...");

	}
	
	else
		printf("No backlash compensation selected. You are fine i guess.\n\nPress any key to exit...");
	fclose(fileread);
	fclose(filewrite);
	return 0;
}


void getFiles(FILE** fileread, FILE** filewrite, soffsets offset, char *filename){
	
	//Filenames
	char *fn = filename;									//Filename without .gcode
	char fnr[256] = "";									//Filename to read from
	char fnw[256] = "";									//Filename to save to	
	sprintf(fnr,"%s.gcode",fn);
	sprintf(fnw,"%s__ABL.gcode",fn);
	
	printf("\n\n%s\n\n", fnw);

	if (!(*fileread = fopen (fnr, "r")))				//try open
	{
		printf("File doesn't exist.\n");
		exit(2);
	}

	*filewrite = fopen (fnw, "w");							//create new file
		
}

soffsets getOffsets(float xoffset, float yoffset){
	soffsets offsets;												//soffset x and y are saved here
		
	offsets.x = getOffset('X', xoffset);										//get new offsets
	offsets.y = getOffset('Y', yoffset);
	
	return offsets;
}

soffset getOffset(char coord, float val){
	soffset offset;
	offset.change = false;
	do {
		printf("Please enter your desired backlash compensation in %c (0.000 - 2.000 mm): ", coord);
		if (val < 0.0)
			printf("can't be negativ\n");
		else if (val > 2.0)
			printf("too big\n");
		
	} while (val < 0.0 || val > 2.0);
	val = roundf(val*1000)/1000;
	if(val != 0.0) offset.change = true;
	printf("%c-Axis Compensation: %.3f mm\n\n", coord, val);
	
	offset.val = val;
	
	return offset;
}

sline getNewLine(FILE** fileread, bool G91){
	sline line = plainLine();										//generate new empty line							
	
	int pos = 0;
	line.readOK = fgets (line.read, sizeof line.read, *fileread);	//read next line
	line.isG91Active = G91;											//copy G91 status from last line
	//Analyse new Line if read was OK
	if (line.readOK){
			
		while (line.read[pos] == ' ') pos++;				//skip spaces
		
		if ((line.read[pos] == 'G' && line.read[pos+1] == '9' && line.read[pos+2] == '0')){//G90 detected - start converting
				line.G90 = true;
		}
		
		if (line.isG91Active){										//G91 was active befor, look for G90 or skip line
			if ((line.read[pos] == 'G' && line.read[pos+1] == '9' && line.read[pos+2] == '0')){//G90 detected - back to normal
				line.isG91Active = false;
			}	
		}
		
		else {
			if (line.read[pos] == 'G' && line.read[pos+1] == '9' && line.read[pos+2] == '1'){	//G91 detected - skip lines until G90 comes up
				line.isG91Active = true;
			}	
			else if (line.read[pos] == 'G' && (line.read[pos+1] == '0' || line.read[pos+1] == '1') && line.read[pos+2] == ' '){		//Absolute G0/G1 move detected
				pos++;																				//Go to 0 or 1 of G0/G1
				line.G = line.read[pos] - '0';														//Save G type

				while (line.read[pos]){																//check whole line
					switch(line.read[pos]){
						case 'F':																	//Speed set
							line.seenF = true;
							line.F = getiValue(line.read, pos+1);
							if(!isdigit(line.read[pos+1])) line.isErrorPossible = true;
							break;
						case 'X':																	//X move
							line.seenX = true;
							line.X = getValue(line.read, pos+1);
							if(!isdigit(line.read[pos+1])) line.isErrorPossible = true;
							break;
						case 'Y':																	//Y move
							line.seenY = true;	
							line.Y = getValue(line.read, pos+1);
							if(!isdigit(line.read[pos+1])) line.isErrorPossible = true;
							break;
						case 'Z':																	//Z move
							line.seenZ = true;
							line.Z = getValue(line.read, pos+1);
							if(!isdigit(line.read[pos+1])) line.isErrorPossible = true;
							break;
						case 'E':																	//E move
							line.seenE = true;
							line.E = getValue(line.read, pos+1);
							if(!isdigit(line.read[pos+1])) line.isErrorPossible = true;
							break;	
					}				
					pos++;																			//next char
				}
			}
		}
	}

	return line;	
}

int getiValue(char read[256], int pos){
	int val = 0;
	if(!isdigit(read[pos]))	pos++;						//First char after command is no digit, Error?(no value, + sign, negativ number) - skip and continue
	
	
	while (isdigit(read[pos])){
		val = val*10 + read[pos] - '0';					//Convert str to Value
		pos++;
	}
	
	return val;
}

float getValue(char read[256], int pos){
	float val = 0.0;
	int c = 10;
	
	if(!isdigit(read[pos])) pos++;										//First char after command is no digit, Error?(no value, + sign, negativ number) - skip and continue

	while (isdigit(read[pos])){											//get whole numbers
		val = val*10 + read[pos] - '0';									//Convert str to Value
		pos++;
	}
	if (read[pos] == '.'){												//floating point
		pos++;
		while (isdigit(read[pos])){										//get numbers after floating point
			val = val + (float)(read[pos] - '0')/c;						//Convert str to Value
			c = c*10;
			pos++;
		}
	}
	return val;
	
}

sline generateLine(sline line){
	sprintf(line.dummy, "G%d ", line.G);
	strcpy(line.write, line.dummy);
	
	if (line.seenF){
		sprintf(line.dummy, "F%d ", line.F);
		strcat(line.write, line.dummy);
	}
	if (line.seenX){
		sprintf(line.dummy, "X%.3f ", line.nX);
		strcat(line.write, line.dummy);
	}
	if (line.seenY){
		sprintf(line.dummy, "Y%.3f ", line.nY);
		strcat(line.write, line.dummy);
	}
	if (line.seenZ){
		sprintf(line.dummy, "Z%.3f ", line.Z);
		strcat(line.write, line.dummy);
	}
	if (line.seenE){
		sprintf(line.dummy, "E%.5f ", line.E);
		strcat(line.write, line.dummy);
	}
	strcat(line.write, "\n");
	
	return line;
}

sline addbacklash(sline line, soffsets offset, scoord coord){
	//X COORDS
	if (line.seenX && offset.x.change){
		if (coord.blX){											//backlash active - last movement was positiv
			if ((line.X + offset.x.val) >= coord.x){			//positiv or no movement - backlash stays
				line.nX = line.X + offset.x.val;
				line.blX = true;
			}
			else if ((line.X + offset.x.val) < coord.x){		//negativ movement - backlash reversed
				line.nX = line.X;
				line.blX = false;
				line.blXchange = true;							//backlash changed -> insert travelmove if extruder is active
			}
		}
		else {													//backlash not active - last movement was negativ
			if (line.X > coord.x){								//positiv movement - backlash added
				line.nX = line.X + offset.x.val;
				line.blX = true;
				line.blXchange = true;							//backlash changed -> insert travelmove if extruder is active
			}
			else if (line.X <= coord.x){						//negativ or no movement - backlash stays off
				line.nX = line.X;
				line.blX = false;
			}
		}
	}
	else if (line.seenX)
		line.nX = line.X;										//no change to X, c/p
	//Y COORDS
	if (line.seenY && offset.y.change){
		if (coord.blY){											//backlash active - last movement was positiv
			if ((line.Y + offset.y.val) >= coord.y){			//positiv or no movement - backlash stays
				line.nY = line.Y + offset.y.val;
				line.blY = true;
			}
			else if ((line.Y + offset.y.val) < coord.y){		//negativ movement - backlash reversed
				line.nY = line.Y;
				line.blY = false;
				line.blYchange = true;							//backlash changed -> insert travelmove if extruder is active
			}
		}
		else {													//backlash not active - last movement was negativ
			if (line.Y > coord.y){								//positiv movement - backlash added
				line.nY = line.Y + offset.y.val;
				line.blY = true;
				line.blYchange = true;							//backlash changed -> insert travelmove if extruder is active
			}
			else if (line.Y <= coord.y){						//negativ or no movement - backlash stays off
				line.nY = line.Y;
				line.blY = false;
			}
		}
	}
	else if (line.seenY)
		line.nY = line.Y;										//no change to Y, c/p
	
	return line;
}

sline applyTravel(sline line, soffsets offset, scoord coord){
	//X
	if (offset.x.change){								//x backlash
		if (line.blXchange){							//x backlash direction change
			if(coord.blX)								//x backlash was active last movement - revert
				line.nX = coord.x - offset.x.val;				
			else										//x backlash was inactive last movement - add
				line.nX = coord.x + offset.x.val;										
		}
		else											//no x backlash direction change, c/p last x coord
			line.nX = coord.x;		
	}
	else												//no x backlash, just c/p last x coord
		line.nX = coord.x;
	
	//Y	
	if (offset.y.change){								//y backlash
		if (line.blYchange){							//y backlash direction change
			if(coord.blY)								//y backlash was active last movement - revert
				line.nY = coord.y - offset.y.val;				
			else										//y backlash was inactive last movement - add
				line.nY = coord.y + offset.y.val;										
		}
		else											//no y backlash direction change, c/p last y coord
			line.nY = coord.y;		
	}
	else												//no y backlash, just c/p last y coord
		line.nY = coord.y;
	
	//generate travel line
	
	sprintf(line.dummy, "G%d ", line.G);
	strcpy(line.write, line.dummy);
	
	if (line.seenF){
		sprintf(line.dummy, "F%d ", line.F);
		strcat(line.write, line.dummy);
	}
	if (line.seenX){
		sprintf(line.dummy, "X%.3f ", line.nX);
		strcat(line.write, line.dummy);
	}
	if (line.seenY){
		sprintf(line.dummy, "Y%.3f ", line.nY);
		strcat(line.write, line.dummy);
	}
	//NO Z MOVEMENT YET!
	//NO E MOVEMENT YET!
	
	strcat(line.write, ";BL\n");						//Add comment so these lines can be found in the file
	
	return line;
}

sline plainLine(){
	sline line;
	
	strcpy(line.read, "");
	strcpy(line.write, "");
	strcpy(line.dummy, "");										
	line.G = 0;
	line.F = 0;												
	line.X = 0.0;
	line.Y = 0.0;
	line.Z = 0.0;
	line.E = 0.0;
	line.nX = 0.0;
	line.nY = 0.0;
	line.seenF = false;
	line.seenX = false;
	line.seenY = false;
	line.seenZ = false;
	line.seenE = false;
	line.isErrorPossible = false;										
	line.isG91Active = false;											
	line.readOK = false;
	line.blX = false;
	line.blY = false;
	line.blXchange = false;
	line.blYchange = false;
	line.G90 = false;
		
	return line;
}
