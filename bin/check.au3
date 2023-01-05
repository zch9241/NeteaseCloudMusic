;¼ì²â´°¿Ú
Global $var = WinWait('[CLASS:OrpheusBrowserHost]', '', 1)
Global $f = 1
While $f
   If $var == 0 Then
	  Run("notify.bat")
	  $flag = MsgBox(5,'check.exe','Î´¼ì²âµ½ÍøÒ×ÔÆ´°¿Ú')
	  if $flag == 2 Then
		 $f = 0
		 EndIf
   EndIf
   Sleep(1000)
WEnd