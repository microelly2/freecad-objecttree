# freecad-objecttree

A plugin for freecad to browse the object hierarchy 


#Linux Installation Instructions

-copy the icons from the icons folder into /usr/lib/freecad/Mod/plugins/icons
-download the objecttree.py into your macro folder
-execute this python file as a macro or paste it into the python console 


#Usage

You have to open a FreeCAD file and select one object

- Refresh - recomputes the familiy view (parents and childrens with depth 2)
- Parents -  recomputes the parents view. This view displays all object the selected one depends on.
- Children - recomputes the children view. This vies displays all objects that are derived from the selected one.
- Snapshot - generates a png-File of a calculated view for documentation purposes. You have to save the file by yourself,
it is overwritten next time you call this function
- Props - opens the Property view  for the selected object. So you can read/modify the objects data.
- Search - here you can look for an object by its name. You can use a search pattern to restrict the list of possibilities. 
The pattern string uses the regular expression syntax for sophisticated queries. In most cases you will type in a substring. 
Note that the filter is case sensitive.
- green Plus - Unfold a subtree on this place

If you select an object in the tree view - it is selected in the FreeCAD environment too. 
If you change the selection in the FreeCAD env you have to refresh the view using one of the update buttons.


#Open, Todos

- change the direction of the display 
- make parameteres configurable (width of the family view, format snapshot, ...)
- port to other oparating systems
- better icon access
