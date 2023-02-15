! Description:
! Definition of a body load.
module m_bload
    implicit none
    
    private
    public t_bload, new_bload
    
    type t_bload
        integer   :: i_eset        ! index of element set
        character :: t_bload       ! type of body load ('A': acceleration, 'F': body force)
        real      :: components(3) ! body load components
    end type
    
    interface new_bload
        module procedure :: constructor
    end interface
    
    contains
    
    ! Description:
    ! Body load constructor.
    type(t_bload) function constructor(i_eset, t_bload, x, y, z) result(self)
        integer,   intent(in) :: i_eset  ! index of element set
        character, intent(in) :: t_bload ! type of body load ('A': acceleration, 'F': body force)
        real,      intent(in) :: x, y, z ! body load components
        self%i_eset     = i_eset
        self%t_bload    = t_bload
        self%components = [x, y, z]
    end function
    
end module
