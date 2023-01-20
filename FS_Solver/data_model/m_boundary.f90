! Description:
! Definition of a boundary condition.
module m_boundary
    implicit none
    
    private
    public t_boundary, new_boundary
    
    type t_boundary
        integer :: i_nset        ! index of node set
        real    :: components(3) ! boundary condition components
        logical :: active(3)     ! boundary condition active flags
    end type
    
    interface new_boundary
        module procedure :: constructor
    end interface
    
    contains
    
    ! Description:
    ! Boundary condition constructor.
    type(t_boundary) function constructor(i_nset, x, y, z, active_x, active_y, active_z) result(this)
        integer, intent(in) :: i_nset                       ! index of node set
        real,    intent(in) :: x, y, z                      ! boundary condition components
        logical, intent(in) :: active_x, active_y, active_z ! boundary condition active flags
        this%i_nset     = i_nset
        this%components = [x, y, z]
        this%active     = [active_x, active_y, active_z]
    end function
    
end module
