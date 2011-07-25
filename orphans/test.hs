type Function = Double -> Double
type Bijection = (Function, Function)

linspace a b = (\x -> m * x - a, \x -> range*x + a)
    where m = 1.0 / range
          range = b - a
	  
type Cursor = (Double, [Bijection])

