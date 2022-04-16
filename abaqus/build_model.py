# === Modules ===

from part import *
from material import *
from section import *
from assembly import *
from step import *
from regionToolset import *
from interaction import *
from load import *
from mesh import *
from job import *
from sketch import *
from visualization import *
from connectorBehavior import *

'''
[x] switch from Pa to MPa
[x] adapt for elastic only
[x] check that fracture still works
[ ] meshing options
[x] match geometry from XFEM mode 1 example
[x] flip references points
[x] add additional strain measures: E, NE, LE
[x] extrapolate averaged integration point quantities to nodes

'''
#---------------------------------------------------------------------------------
# === Parameters ===
modelName_1 = 'tension'

length = 3000.0                              # plate half-length (mm)
height = 3000.0                              # plate height (mm)
width  = 1000.0                              # plate width (mm)

crack_len = 300.0                           # crack length (mm)
crack_y   = 0.0                          # crack offset in y-direction (mm)

YM    = 210000.0                          # Young's modulus
NU    = 0.3                               # Poisson's ratio
MAXPS = 220.0                          # Damage initiation (MPa)
DTOL  = 0.05                              # Damage tolerance
GI    = 42.2                           # Fracture energy (N/mm)
ETA   = 1.0                               # Power-law exponent

disp = 2.0

option = 2          # 1 for elastic only
                    # 2 for xfem

#---------------------------------------------------------------------------------
# === Create model ===
Mdb()

if option == 1:
    modelName_2 = 'elastic'
elif option == 2:
    modelName_2 = 'fracture'
else:
    print('Specify valid option')
    
modelName = modelName_1 + '_' + modelName_2

viewportName = session.Viewport(name=modelName)
viewportName.makeCurrent()
viewportName.maximize()

plateModel = mdb.Model(name=modelName)
del mdb.models['Model-1']

#---------------------------------------------------------------------------------
# === Create parts ===
plateSketch = plateModel.ConstrainedSketch(name='plateProfile',sheetSize=height)
plateSketch.setPrimaryObject(option=STANDALONE)
plateSketch.sketchOptions.setValues(decimalPlaces=3)
plateSketch.Line(point1=(0.0, -height/2.0), point2=(0.0, height/2.0))
plateSketch.Line(point1=(0.0, height/2.0), point2=(length, height/2.0))
plateSketch.Line(point1=(length, height/2.0), point2=(length, -height/2.0))
plateSketch.Line(point1=(length, -height/2.0), point2=(0.0, -height/2.0))
platePart = plateModel.Part(dimensionality=TWO_D_PLANAR, name='plate', 
                type=DEFORMABLE_BODY)
platePart.BaseShell(sketch=plateModel.sketches['plateProfile'])
plateSketch.unsetPrimaryObject()
del plateSketch


# Part for crack geometry
if option == 2:
    crackSketch =  plateModel.ConstrainedSketch(name='crackProfile',sheetSize=height)
    crackSketch.Line(point1=(0.0, crack_y), point2=(crack_len, crack_y))
    crackPart = plateModel.Part(dimensionality=TWO_D_PLANAR, name='crack',
                    type=DEFORMABLE_BODY)
    crackPart.BaseWire(sketch=plateModel.sketches['crackProfile'])
    crackSketch.unsetPrimaryObject()
    del crackSketch

#---------------------------------------------------------------------------------

# === Create geometry sets ===
platePart.Set(faces=platePart.faces[:], name='All')
e1  = platePart.edges.findAt(( (length/2.0,  -height/2.0, 0.0), ))
platePart.Set(edges=e1, name='bottom')
e1  = platePart.edges.findAt(( (length/2.0,  +height/2.0, 0.0), ))
platePart.Set(edges=e1, name='top')
e1  = platePart.edges.findAt(( (length, 0.0, 0.0), ))
platePart.Set(edges=e1, name='right')

#---------------------------------------------------------------------------------
# === Define material and section properties ===
plateMatl = plateModel.Material(name='elas')
plateMatl.Elastic(table=((YM, NU), ))
if option == 2:
    plateMatl.MaxpsDamageInitiation(table=((MAXPS, ), ), tolerance=DTOL)
    plateMatl.maxpsDamageInitiation.DamageEvolution(
        mixedModeBehavior=POWER_LAW, power=ETA, table=((GI, GI, 0.0), ), type=ENERGY)
    plateMatl.maxpsDamageInitiation.DamageStabilizationCohesive(
        cohesiveCoeff=0.00001)

plateModel.HomogeneousSolidSection(material='elas', name='solid', thickness=width)

#---------------------------------------------------------------------------------
# === Assign section and orientation ===
platePart.MaterialOrientation(fieldName='', localCsys=None, orientationType=GLOBAL, region=
    platePart.sets['All'], stackDirection=STACK_3)

platePart.SectionAssignment(region=platePart.sets['All'], sectionName='solid')

#---------------------------------------------------------------------------------
# === Assign mesh controls and mesh plate ===
# Element type
platePart.setElementType(elemTypes=(ElemType(elemCode=CPE4, elemLibrary=STANDARD), 
    ElemType(elemCode=CPE3, elemLibrary=STANDARD)), regions=platePart.sets['All'])

# Mesh technique
platePart.setMeshControls(elemShape=QUAD, regions=platePart.faces[:], technique=STRUCTURED)

# Seed mesh
ex = 30;  ey = 59;
e1 = platePart.edges.findAt(( (length/2.0, -height/2.0, 0.0), ))
platePart.seedEdgeByNumber(edges=e1, number=ex)
e1 = platePart.edges.findAt(( (length, 0.0, 0.0), ))
platePart.seedEdgeByNumber(edges=e1, number=ey)
platePart.generateMesh()

# === End part ===

#---------------------------------------------------------------------------------
# === Assemble ===
plateModel.rootAssembly.DatumCsysByDefault(CARTESIAN)
plateModel.rootAssembly.Instance(dependent=ON, name='plate_1', part=platePart)
if option == 2:
    plateModel.rootAssembly.Instance(dependent=ON, name='crack_1', part=crackPart)

# Reference points for displacement application
rp_db = plateModel.rootAssembly.ReferencePoint(point=(length/2, height/2.0, 
    0.0))
plateModel.rootAssembly.features.changeKey(fromName='RP-1', toName='db')

#---------------------------------------------------------------------------------
# === Create assembly sets ===
v1 = (plateModel.rootAssembly.referencePoints[rp_db.id], )
plateModel.rootAssembly.Set(name='bdisp', referencePoints=v1)

# === End assembly ===

#---------------------------------------------------------------------------------
# === Create constraint equation ===
plateModel.Equation(name='ce_bot', terms=((1.0, 'plate_1.top', 2), (-1.0, 'bdisp', 2)))

#---------------------------------------------------------------------------------
# === Create step ===
plateModel.StaticStep(timePeriod=0.8, initialInc=0.01, maxInc=0.01, maxNumInc=10000,
    minInc=1e-09, name='Static', nlgeom=ON, previous='Initial')

plateModel.steps['Static'].control.setValues(
    allowPropagation=OFF, discontinuous=ON, resetDefaultValues=OFF, 
    timeIncrementation=(8.0, 10.0, 9.0, 16.0, 10.0, 4.0, 12.0, 20.0, 6.0, 3.0, 
    50.0))
    
if option == 1:
    plateModel.fieldOutputRequests['F-Output-1'].setValues(
        variables=('S', 'LE', 'U', 'RF', 'E', 'NE'), 
        position=AVERAGED_AT_NODES)
if option == 2:
    plateModel.fieldOutputRequests['F-Output-1'].setValues(
        variables=('S', 'LE', 'U', 'RF', 'PHILSM', 'STATUSXFEM', 'E', 'NE'),
        position=AVERAGED_AT_NODES)

plateModel.HistoryOutputRequest(createStepName='Static', 
    name='H-Output-2', rebar=EXCLUDE, region=
    mdb.models[modelName].rootAssembly.sets['bdisp'], sectionPoints=
    DEFAULT, variables=('U2', 'RF2'))

#---------------------------------------------------------------------------------
# === Apply boundary conditions ===
# plateModel.DisplacementBC(amplitude=UNSET, createStepName=
    # 'Static', distributionType=UNIFORM, fieldName='', fixed=OFF, localCsys=None
    # , name='rp', region=plateModel.rootAssembly.sets['bdisp'], u1=0, u2=
    # UNSET, ur3=0)

plateModel.DisplacementBC(amplitude=UNSET, createStepName=
    'Static', distributionType=UNIFORM, fieldName='', fixed=OFF, localCsys=None
    , name='top', region=plateModel.rootAssembly.sets['bdisp']
    , u1=UNSET, u2=0.5*disp, ur3=UNSET)

plateModel.DisplacementBC(amplitude=UNSET, createStepName=
    'Static', distributionType=UNIFORM, fieldName='', fixed=OFF, localCsys=None
    , name='bot', region=plateModel.rootAssembly.instances['plate_1'].sets['bottom']
    , u1=UNSET, u2=-0.5*disp, ur3=UNSET)

plateModel.DisplacementBC(amplitude=UNSET, createStepName=
    'Static', distributionType=UNIFORM, fieldName='', fixed=OFF, localCsys=None
    , name='side', region=plateModel.rootAssembly.instances['plate_1'].sets['right']
    , u1=0.0, u2=UNSET, ur3=UNSET)
    
#---------------------------------------------------------------------------------
# === Define enrichment and initial crack ===
if option == 2:
    edges = plateModel.rootAssembly.instances['crack_1'].edges
    e1 = edges.findAt(( (crack_len/2.0, crack_y, 0.0), ))
    crackLocation = Region(edges=e1)

    plateModel.ContactProperty('contact')
    plateModel.interactionProperties['contact'].GeometricProperties(
        contactArea=0.02, padThickness=None)
    plateModel.rootAssembly.engineeringFeatures.XFEMCrack( name='enr1',
        crackDomain=plateModel.rootAssembly.instances['plate_1'].sets['All']
        , interactionProperty='contact', crackLocation=crackLocation)


#---------------------------------------------------------------------------------
# === Create Job === 
jobName = modelName + '_job'
mdb.Job(model=modelName, name=jobName)


#---------------------------------------------------------------------------------


