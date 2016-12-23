SELECT (
	SELECT(
		   CASE 
		    WHEN (yearAbove - yearBelow) = 0 THEN belowVal 
		    ELSE belowVal + ((aboveVal - belowVal)/ NULLIF((yearAbove - yearBelow), 0))*(yearBP - yearBelow) 
		   END ) as value
	FROM (
		    SELECT
		      ST_Value(rast, bandBelow, pt) as belowVal,
		      ST_Value(rast, bandAbove, pt) as aboveVal,
		      yearBelow, yearAbove,
		      yearBP, 
		      id 
		FROM 
	    data_d7c09599b8d211e6bef09cf387ae7186
	    WHERE ST_Intersects(rast, pt)) as xvals
 ) as x,
 (
	SELECT(
		   CASE 
		    WHEN (yearAbove - yearBelow) = 0 THEN belowVal 
		    ELSE belowVal + ((aboveVal - belowVal)/ NULLIF((yearAbove - yearBelow), 0))*(yearBP - yearBelow) 
		   END ) as value
	FROM (
		    SELECT
		      ST_Value(rast, bandBelow, pt) as belowVal,
		      ST_Value(rast, bandAbove, pt) as aboveVal,
		      yearBelow, yearAbove,
		      yearBP, 
		      id 
		FROM 
	    data_d7c09599b8d211e6bef09cf387ae7186
	    WHERE ST_Intersects(rast, pt)) as yvals
 ) as y 
  FROM 
      (select p.geom as pt, 
      p.yearBelow as yearBelow, 
      p.yearAbove as yearAbove, 
      p.bandBelow as bandBelow, 
      p.bandAbove as bandAbove,
      p.yr as yearBP, 
      p.id as id 
      from pointrequests as p WHERE callID = 'e87c0e60-b1b5-11e6-832e-db058c7a17cd') as makePoint   ; 
