! Description:
! Definition of a surface load.
module m_sload
    implicit none
    
    private
    public t_sload, new_sload
    
    type t_sload
        integer   :: i_sset        ! index of surface set
        character :: t_sload       ! type of surface load ('P': pressure, 'T': surface traction)
        real      :: components(3) ! surface load components in case of surface traction
        real      :: magnitude     ! surface load magnitude in case of pressure
    end type
    
    interface new_sload
        module procedure :: constructor
    end interface
    
    contains
    
    ! Description:
    ! Surface load constructor.
    type(t_sload) function constructor(i_sset, t_sload, x, y, z) result(self)
        integer,   intent(in) :: i_sset  ! index of surface set
        character, intent(in) :: t_sload ! type of surface load ('P': pressure, 'T': surface traction)
        real,      intent(in) :: x, y, z ! surface load components
        self%i_sset  = i_sset
        self%t_sload = t_sload
        if (self%t_sload == 'P') self%magnitude = x
        if (self%t_sload == 'T') self%components = [x, y, z]
    end function
    
end module
