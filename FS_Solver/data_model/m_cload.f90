! Description:
! Definition of a concentrated load.
module m_cload
    implicit none
    
    private
    public t_cload, new_cload
    
    type t_cload
        integer :: i_nset        ! index of node set
        real    :: components(3) ! concentrated load components
    end type
    
    interface new_cload
        module procedure :: constructor
    end interface
    
    contains
    
    ! Description:
    ! Concentrated load constructor.
    type(t_cload) function constructor(i_nset, x, y, z) result(this)
        integer, intent(in) :: i_nset  ! index of node set
        real,    intent(in) :: x, y, z ! concentrated load components
        this%i_nset     = i_nset
        this%components = [x, y, z]
    end function
    
end module
