store-stats
================

The following script prints the folder stat per store

## Usage

#### List per user

    python store-stats -u <username> 

#### show store summary 

    python store-stats -u <username> --summary
    
#### List for public store

    python store-stats --public
    
#### List multiple users 

    python store-stats -u <username>  -u <username> 
    
#### List hidden folders 

    python store-stats -u <username>  --hidden

#### Only count items older then

    python store-stats -u <username>  --older-then "dd-mm-yyyy 00:00"